from django.core.management.base import BaseCommand
from django.db import transaction
from django.apps import apps
import json
import os


class Command(BaseCommand):
    help = "Update field values in any table based on mapping"

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            type=str,
            help='Model name (e.g., CategoryIconName, Program, etc.)'
        )
        parser.add_argument(
            'field',
            type=str,
            help='Field name to update'
        )
        parser.add_argument(
            'mapping_file',
            type=str,
            help='JSON file containing old->new value mappings'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )

    def handle(self, *args, **options):
        try:
            # Get the model class dynamically
            app_label = 'programs'  # Default to programs app
            model_name = options['model']
            Model = apps.get_model(app_label, model_name)
            
            # Get absolute path for the mapping file
            mapping_file = options['mapping_file']
            if not os.path.isabs(mapping_file):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                mapping_file = os.path.join(base_dir, mapping_file)

            # Load the mapping file
            with open(options['mapping_file'], 'r') as f:
                value_mapping = json.load(f)

            field_name = options['field']
            dry_run = options['dry_run']

            self.stdout.write(f"Updating {model_name}.{field_name} values...")

            with transaction.atomic():
                updated_count = 0
                for old_value, new_value in value_mapping.items():
                    # Create filter kwargs dynamically
                    filter_kwargs = {
                        f"{field_name}__iexact": old_value
                    }
                    
                    # Create update kwargs dynamically
                    update_kwargs = {
                        field_name: new_value
                    }

                    # Get matching records
                    records = Model.objects.filter(**filter_kwargs)
                    count = records.count()
                    
                    if count:
                        if dry_run:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Would update "{old_value}" to "{new_value}" ({count} records)'
                                )
                            )
                        else:
                            records.update(**update_kwargs)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Updated "{old_value}" to "{new_value}" ({count} records)'
                                )
                            )
                        updated_count += count

                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Would update {updated_count} records (dry run)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully updated {updated_count} records'
                        )
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error updating values: {str(e)}'
                )
            )