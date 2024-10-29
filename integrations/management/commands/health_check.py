from django.core.management.base import BaseCommand
from django.conf import settings
from decouple import config
from hubspot import HubSpot
from hubspot.crm.contacts.exceptions import ForbiddenException
from django.db.models import Q
from authentication.models import User
from integrations.models import Link
from programs.models import Navigator, Program, UrgentNeed
from translations.models import BLANK_TRANSLATION_PLACEHOLDER, Translation
import argparse


class Command(BaseCommand):
    help = "Check that we can't read from HubSpot, and there is no PII in the database"

    HUB_SPOT_TEXT = "Can't read Hub Spot"
    PII_IN_DB_TEXT = "PII not in the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--strict",
            action=argparse.BooleanOptionalAction,
            help="Should the he website hashes should be compared to the old hashes",
        )

    def handle(self, *args, **options):
        self.stdout.write("")

        self._check_links(options["strict"])

        self.stdout.write("")

        self._output_condition(self._cant_read_hubspot(), self.HUB_SPOT_TEXT)
        self._output_condition(self._no_pii_in_db(), self.PII_IN_DB_TEXT)

    def _cant_read_hubspot(self) -> bool:
        client = HubSpot(access_token=config("HUBSPOT"))

        try:
            client.crm.contacts.basic_api.get_page(limit=1, archived=False)
            return False
        except ForbiddenException as e:
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception when calling basic_api->get_page: {e}"))
            return False

    def _no_pii_in_db(self) -> bool:
        users = User.objects.filter(is_staff=False).filter(
            Q(first_name__isnull=False)
            | Q(last_name__isnull=False)
            | Q(cell__isnull=False)
            | Q(email__isnull=False)
            | Q(external_id__isnull=True)
        )

        if len(users) > 0:
            return False
        return True

    def _check_links(self, strict: bool = False) -> bool:
        links = self._get_links()

        Link.objects.all().update(in_use=False)

        for link in links:
            if link == BLANK_TRANSLATION_PLACEHOLDER or link == "":
                continue

            try:
                link_model: Link = Link.objects.get(link=link)
                link_model.in_use = True
                link_model.save()
            except Link.DoesNotExist:
                link_model: Link = Link.objects.create(link=link, validated=False, in_use=True)

            link_model.validate()

            if strict:
                valid = link_model.validated
            else:
                valid = Link.good_status_code(link_model.status_code)

            self._output_condition(valid, f"{link} {link_model.status_code}")

    def _get_links(self) -> list[str]:
        program_links = [p.apply_button_link for p in Program.objects.filter(active=True)]
        urgent_need_links = [u.link for u in UrgentNeed.objects.filter(active=True)]
        navigator_links = [n.assistance_link for n in Navigator.objects.filter(programs__isnull=False)]

        links = {
            *self._get_translation_links(program_links),
            *self._get_translation_links(urgent_need_links),
            *self._get_translation_links(navigator_links),
        }

        return list(links)

    def _get_translation_links(self, translations: list[Translation]) -> list[str]:
        links = set()
        for translation in translations:
            for lang_setting in settings.LANGUAGES:
                lang = lang_setting[0]
                translation.set_current_language(lang)

                links.add(translation.text)

        return list(links)

    def _output_condition(self, validated: bool, message: str):
        text = f"{message}: {'VALIDATED' if validated else 'FAILED'}"

        if validated:
            self.stdout.write(self.style.SUCCESS(text))
        else:
            self.stdout.write(self.style.ERROR(text))
