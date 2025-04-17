from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from programs.models import Program
from screener.models import WhiteLabel
from configuration.white_labels import white_label_config


class Command(BaseCommand):
    help = "Transfer programs from one white label to another"

    def add_arguments(self, parser):
        parser.add_argument(
            "target_white_label",
            type=str,
            help="The white label code to transfer programs to target whilte label",
        )
        parser.add_argument(
            "external_names",
            nargs="+",
            type=str,
            help="External names of programs to transfer",
        )

    def validate_white_label(self, white_label_code):
        """Validate white label exists in config and database"""
        if white_label_code not in white_label_config:
            self.stdout.write(
                self.style.ERROR(
                    f"White label '{white_label_code}' not found in configuration. "
                    f"Please run: python manage.py add_config {white_label_code}"
                )
            )
            return False

        try:
            WhiteLabel.objects.get(code=white_label_code)
            return True
        except ObjectDoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f"White label '{white_label_code}' not found in database. "
                    f"Please ensure it's configured properly."
                )
            )
            return False

    @transaction.atomic
    def handle(self, *args, **options):
        target_code = options["target_white_label"]
        external_names = options["external_names"]

        # Validate white label exists
        if not self.validate_white_label(target_code):
            return

        target_white_label = WhiteLabel.objects.get(code=target_code)

        for external_name in external_names:
            try:
                # Get source program
                source_program = Program.objects.get(external_name=external_name)

                # Check if program already exists
                new_external_name = f"{target_code}_{external_name.split('_')[-1]}"
                if Program.objects.filter(white_label=target_white_label, external_name=new_external_name).exists():
                    print(f"Program already exists in {target_code} with name {new_external_name}")
                    continue

                legal_statuses = source_program.legal_status_required.all()

                # Create new program
                new_program = source_program
                new_program.pk = None
                new_program.white_label = target_white_label
                new_program.external_name = new_external_name
                new_program.year = source_program.year

                # Save new program
                new_program.save()

                # Then set the many-to-many relationship
                new_program.legal_status_required.set(legal_statuses)

            except Program.DoesNotExist:
                print(f"Error: Program '{external_name}' not found")
                continue
            except Exception as e:
                print(f"Error during transfer: {str(e)}")
                continue
