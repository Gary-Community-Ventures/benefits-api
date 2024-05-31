from django.core.management.base import BaseCommand
from programs.models import Program, FederalPoveryLimit


class Command(BaseCommand):
    help = "Update FPL field for all programs to this year's FederalPoveryLimit"

    def handle(self, *args, **options):
        fpl_this_year = FederalPoveryLimit.objects.get(year="THIS YEAR")

        Program.objects.update(fpl=fpl_this_year)

        self.stdout.write(self.style.SUCCESS("Successfully updated FPL field for all programs"))
