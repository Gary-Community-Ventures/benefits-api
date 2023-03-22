from django.core.management.base import BaseCommand
from screener.models import Screen
from screener.views import eligibility_results


class Command(BaseCommand):
    help = '''
    Creates snapshots for all users.
    Limit default is 1.
    Defaults to only creating snapshots for users with emails.
    '''

    def add_arguments(self, parser):
        parser.add_argument('--limit', default=1, type=int)
        parser.add_argument('--all', default=False, type=bool)

    def handle(self, *args, **options):
        # Get the screens
        screens = Screen.objects.filter(
            agree_to_tos=True,
            is_test=False,
        )

        if not options['all']:
            screens = screens.exclude(user__isnull=True)

        # [:None] is everything
        limit = None if options['limit'] == -1 else options['limit']
        screens = screens.order_by('-submission_date')[:limit]

        # Calculate eligibility for each screen
        for screen in screens:
            eligibility_results(screen, batch=True)
