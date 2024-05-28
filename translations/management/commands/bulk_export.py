from django.core.management.base import BaseCommand
from translations.models import Translation
import json


class Command(BaseCommand):
    help = """
    Get translation export
    """

    def handle(self, *args, **options) -> str:
        self.stdout.reconfigure(encoding="utf-8")
        return json.dumps(Translation.objects.export_translations(), ensure_ascii=False)
