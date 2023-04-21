from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from screener.models import Screen, EligibilitySnapshot
from integrations.services.hubspot.integration import Hubspot


class Command(BaseCommand):
    help = '''
    Update number of new benefits and amount of new benefits in HubSpot
    '''

    def add_arguments(self, parser):
        parser.add_argument('--limit', default=1, type=int)

    def handle(self, *args, **options):
        screens = Screen.objects.all().exclude(user__isnull=True)
        latest_snapshots = []
        limit = options['limit']
        for screen in screens:
            try:
                previous_snapshot = EligibilitySnapshot.objects \
                    .filter(is_batch=True, screen=screen) \
                    .latest('submission_date')
            except ObjectDoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'No snapshots for screen with id of {screen.id}')
                )
                continue
            latest_snapshots.append(previous_snapshot)

        hubspot = Hubspot()
        existing_users = []
        for snapshot in latest_snapshots:
            if limit == 0:
                break
            if snapshot.screen.user.external_id is None:
                continue

            num_eligible = 0
            value = 0
            for program in snapshot.program_snapshots.all():
                if program.new and program.eligible:
                    num_eligible += 1
                    value += program.estimated_value

            existing_users.append(hubspot.format_email_new_benefit(snapshot.screen.user, num_eligible, value))

            limit -= 1

        if not len(existing_users):
            self.stdout.write(
                self.style.WARNING('No users in HubSpot. Make sure that you add users to HubSpot first')
            )
            return

        hubspot.bulk_update(existing_users)
