from django.core.management.base import BaseCommand
from translations.bulk_import_translations import bulk_add
from sys import stdin
import argparse
import json


class Command(BaseCommand):
    help = '''
    Get translation export
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            'data', nargs='?', type=argparse.FileType('r', encoding='utf-8'), default=stdin,
        )

    def handle(self, *args, **options):
        print(options['data'].read())
        data = json.loads(options['data'].read())

        bulk_add(data)
