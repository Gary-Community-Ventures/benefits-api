from django.core.management.base import BaseCommand
from programs.models import UrgentNeed
from translations.models import Translation


class Command(BaseCommand):
    help = "Fixes text 'Civil legal needs' in UrgentNeed.type translations"

    def handle(self, *args, **options):
        fixed_count = 0

        urgent_needs = UrgentNeed.objects.select_related("type").all()

        for need in urgent_needs:
            translation = need.type
            if translation.text.strip() == "Civil Legal Needs":
                translation.text = "Civil legal needs"
                translation.save()
                fixed_count += 1

        self.stdout.write(self.style.SUCCESS(f"Fixed capitalization for {fixed_count} urgent needs."))
