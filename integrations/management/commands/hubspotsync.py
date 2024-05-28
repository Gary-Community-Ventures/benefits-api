from django.core.management.base import BaseCommand
from authentication.models import User
from screener.models import Screen
from django.db.models import Q
from integrations.services.hubspot.integration import upsert_user_hubspot
import time
import uuid


class Command(BaseCommand):
    help = "Syncs new users to Hubspot and clears PII from local records"

    def add_arguments(self, parser):
        parser.add_argument("limit", nargs="?", default="1", type=int)

    def handle(self, *args, **options):
        limit = options["limit"]
        status = self.sync_mfb_hubspot_users(limit)
        if len(status["completed"]) > 0:
            self.stdout.write(self.style.SUCCESS("Successfully synced %s users." % len(status["completed"])))
            for message in status["completed"]:
                self.stdout.write(
                    self.style.SUCCESS("Successfully synced user %s with contact %s." % (message[0], message[1]))
                )
        if len(status["failed"]) > 0:
            self.stdout.write(self.style.WARNING("Failed to sync %s users." % len(status["failed"])))
            for message in status["failed"]:
                self.stdout.write(
                    self.style.SUCCESS("Successfully synced user %s with contact %s." % (message[0], message[1]))
                )

    # MFB allows users to sign up to receive benefits updates or offers. If they do
    # so PII is temporarily stored against their user record. This cron function
    # queries the database every 10 minutes for new signups, syncs that data to
    # hubspot, and then clears the PII on the user record in favor of storing the
    # external id. This separates PII from household demographic.
    def sync_mfb_hubspot_users(self, limit):
        status = {"processed": 0, "completed": [], "failed": []}
        screen = None
        processed = 0

        # for now, we only sync users to hubspot who have signed up for offers or
        # updates and given TCPA consent
        unsynced = (
            User.objects.filter(Q(send_offers=True) | Q(send_updates=True))
            .filter(external_id__isnull=True)
            .filter(tcpa_consent=True)
        )

        for user in unsynced:
            if processed < limit:
                user_screens = Screen.objects.filter(user_id=user.id).order_by("-submission_date")
                if user_screens:
                    screen = user_screens.first()
                else:
                    continue
                hubspot_id = upsert_user_hubspot(user, screen)
                if hubspot_id:
                    self.replace_pii_with_hubspot_id(hubspot_id, user)
                    status["completed"].append((user.id, hubspot_id))
                else:
                    status["failed"].append((user.id, hubspot_id))
            # Delay to prevent hitting rate limit of 100 req per 10 seconds
            time.sleep(0.2)
            processed += 1
        return status

    # stores an external id from hubspot and then clears all of the PII
    def replace_pii_with_hubspot_id(self, hubspot_id, user):
        random_id = str(uuid.uuid4()).replace("-", "")
        user.external_id = hubspot_id
        user.email_or_cell = f"{hubspot_id}+{random_id}@myfriendben.org"
        user.first_name = None
        user.last_name = None
        user.cell = None
        user.email = None
        user.save()
        return user
