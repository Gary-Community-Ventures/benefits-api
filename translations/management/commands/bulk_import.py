from django.core.management.base import BaseCommand
from translations.bulk_import_translations import bulk_add
import argparse
import json


class Command(BaseCommand):
    help = '''
    Get translation export
    '''

    def add_arguments(self, parser):
        parser.add_argument('data', type=argparse.FileType('r', encoding='utf8'))

    def handle(self, *args, **options):
        data = json.load(options['data'])

        bulk_add(data)
