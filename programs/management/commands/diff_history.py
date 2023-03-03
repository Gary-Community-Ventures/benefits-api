from django.core.management.base import BaseCommand
from django.conf import settings
import os
import yaml


class Command(BaseCommand):
    help = 'Checks history for changes'

    def compare(self, file):
        with open(file, 'r') as file:
            history = yaml.safe_load(file)

        try:
            latest = history[-1]['eligibility']
            second_latest = history[-2]['eligibility']
        except IndexError:
            print('nothing to compare')
            return

        for key in latest:
            new_eligible = latest[key]['eligibility']
            old_eligible = second_latest[key]['eligibility']

            if new_eligible != old_eligible:
                print(f'    {key}: {old_eligible} => {new_eligible}')

            new_value = latest[key]['value']
            old_value = second_latest[key]['value']

            if new_value != old_value:
                print(f'    {key}: {old_value} => {new_value}')

    def handle(self, *args, **options):
        base_path = os.path.join(settings.BASE_DIR, 'programs', 'program_history')
        for directory in os.listdir(base_path):
            print(directory+':')
            self.compare(os.path.join(base_path, directory, 'history.yaml'))
