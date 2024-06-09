from django.core.management.base import BaseCommand
from django.conf import settings
import os
import yaml


class Command(BaseCommand):
    help = "Checks history for changes"

    def remove_latest(self, path):
        with open(path, "r") as file:
            history = yaml.safe_load(file)

        history = history[:-1]

        with open(path, "w") as file:
            yaml.dump(history, file)

    def handle(self, *args, **options):
        base_path = os.path.join(settings.BASE_DIR, "programs", "program_history")
        for directory in os.listdir(base_path):
            print(directory)
            self.remove_latest(os.path.join(base_path, directory, "history.yaml"))
