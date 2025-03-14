from django.core.management.base import BaseCommand
from programs.models import County
from screener.models import WhiteLabel
from configuration.models import Configuration
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = "Adds counties"

    def add_arguments(self, parser):
        parser.add_argument("white_label", type=str, help="The state code for the white label")

    def handle(self, *args, **options):
        try:
            white_label = WhiteLabel.objects.get(code=options["white_label"])
        except ObjectDoesNotExist:
            self.stdout.write(self.style.WARNING(f'White label for "{options["white_label"]}" is not in the database'))
        try:
            counties_from_config = Configuration.objects.get(name="counties_by_zipcode", white_label=white_label)

            counties = list(set([key for value in eval(counties_from_config.data).values() for key in value.keys()]))

            for county in counties:
                County.objects.get_or_create(name=county, white_label=white_label)
        except ObjectDoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f'"counties_by_zipcode" config object for "{options["white_label"]}" is not in the database'
                )
            )
