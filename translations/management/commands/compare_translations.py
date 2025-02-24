from django.core.management.base import BaseCommand
from datetime import datetime
import argparse
import json
import csv
import os

class Command(BaseCommand):
    help = "Compare translations between source and destination JSON files and generate a report."

    def add_arguments(self, parser):
        parser.add_argument(
            "source_file",
            type=argparse.FileType("r", encoding="utf-8"),
            help="Path to the source translations JSON file"
        )
        parser.add_argument(
            "destination_file",
            type=argparse.FileType("r", encoding="utf-8"),
            help="Path to the destination translations JSON file"
        )

    def handle(self, *args, **options):
        source_data = json.load(options["source_file"]).get("translations", {})
        destination_data = json.load(options["destination_file"]).get("translations", {})
        results = []

        for label, source_details in source_data.items():
            if label not in destination_data:
                """
                Label coming from source file not found in
                the destination file.
                """
                results.append([label, "", "", "", "Not found in destination", "", ""])
                continue
            
            source_langs = source_details.get("langs", {})
            destination_langs = destination_data.get(label, {}).get("langs", {})

            for lang_code, source_message in source_langs.items():
                """
                The JSON file saves the text value for each
                of the languages in the following format:
                "en-us": ["[PLACEHOLDER]", true]
                first element is the text value, second element
                is a boolean indicating if the text was manually
                edited.
                """
                source_text = source_message[0]
                source_edited = source_message[1]

                dest_message = destination_langs.get(lang_code, ["", False])
                destination_text = dest_message[0]
                destination_edited = dest_message[1]

                """
                If source_text and destination_text are empty strings,
                there is no need to compare them, hence they are skipped.
                """
                if source_text == "" and destination_text == "":
                    continue

                if source_text == destination_text:
                    status = "Text matches"
                else:
                    status = "Text different"

                results.append([
                    label,
                    lang_code,
                    source_text,
                    destination_text,
                    status,
                    source_edited,
                    destination_edited
                ])

        self.stdout.write("Generating CSV report...")
        self.generate_csv_report(results)
        self.stdout.write(self.style.SUCCESS("CSV report generated successfully."))

    def generate_csv_report(self, data):
        timestamp = datetime.now().strftime("%I%M%S%p")
        output_file = os.path.join(os.getcwd(), f"translation_sync_report_{timestamp}.csv")

        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Label",
                "Language Code",
                "Source Text",
                "Destination Text",
                "Status",
                "Source Edited",
                "Destination Edited"
            ])
            writer.writerows(data)

        self.stdout.write(f"Report saved to {output_file}")
