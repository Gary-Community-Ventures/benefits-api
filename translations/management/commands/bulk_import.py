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
            'data', nargs='?', type=argparse.FileType('r'), default=stdin
        )

    def handle(self, *args, **options):
        data = json.loads(options['data'].read())

        bulk_add(data)
