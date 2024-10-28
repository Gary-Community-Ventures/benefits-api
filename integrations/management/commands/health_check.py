from django.core.management.base import BaseCommand
from decouple import config
from hubspot import HubSpot
from hubspot.crm.contacts.exceptions import ForbiddenException
from django.db.models import Q

from authentication.models import User


class Command(BaseCommand):
    help = "Check that we can't read from HubSpot, and there is no PII in the database"

    HUB_SPOT_TEXT = "Can read Hub Spot"
    PII_IN_DB_TEXT = "PII in the database"

    def handle(self, *args, **options):
        self.stdout.write("")

        self._output_condition(self._can_read_hubspot(), self.HUB_SPOT_TEXT)
        self._output_condition(self._pii_in_db(), self.PII_IN_DB_TEXT)

    def _can_read_hubspot(self) -> bool:
        client = HubSpot(access_token=config("HUBSPOT"))

        try:
            client.crm.contacts.basic_api.get_page(limit=1, archived=False)
            return True
        except ForbiddenException as e:
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Exception when calling basic_api->get_page: {e}"))
            return True

    def _pii_in_db(self) -> bool:
        users = User.objects.filter(is_staff=False).filter(
            Q(first_name__isnull=False)
            | Q(last_name__isnull=False)
            | Q(cell__isnull=False)
            | Q(email__isnull=False)
            | Q(external_id__isnull=True)
        )

        if len(users) > 0:
            return True
        return False

    def _output_condition(self, condition: bool, message: str):
        text = f"{message}: {condition}"

        if condition:
            self.stdout.write(self.style.ERROR(text))
        else:
            self.stdout.write(self.style.SUCCESS(text))
