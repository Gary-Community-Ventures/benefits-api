from datetime import datetime
from enum import Enum
from random import randint
from typing import Optional
from django.core.management.base import BaseCommand
from googleapiclient.errors import HttpError
from integrations.services.sheets.formatting import color_cell, title_cell, wrap_row
from screener.views import eligibility_results
from validations.models import Validation
from decouple import config
from integrations.services.sheets import GoogleSheets
import argparse


class Result(Enum):
    SKIPPED = "Skipped"
    PASSED = "Passed"
    FAILED = "Failed"


class ValidationResult:
    COLORS = {
        Result.SKIPPED: {"red": 0.5, "green": 0.5, "blue": 0.5},
        Result.PASSED: {"red": 0, "green": 1, "blue": 0},
        Result.FAILED: {"red": 1, "green": 0, "blue": 0},
    }

    def __init__(
        self,
        uuid: str,
        program_name: str,
        result: Result,
        program_id: Optional[int] = None,
        expected_value: int = 0,
        value: int = 0,
        expected_eligibility: bool = False,
        eligibility: bool = False,
    ):
        self.uuid = uuid
        self.program_name = program_name
        self.result = result
        self.program_id = program_id
        self.expected_value = expected_value
        self.value = value
        self.expected_eligibility = expected_eligibility
        self.eligibility = eligibility

    def format_url(self):
        front_end_domain = config("FRONTEND_DOMAIN")
        program_id = ""
        if self.program_id is not None:
            program_id = f"/{self.program_id}/"
        return f"{front_end_domain}/{self.uuid}/results/benefits{program_id}?admin=true"

    def format_value_change(self):
        return f"{self.value} => {self.expected_value}"

    def sheets_cell(self, value, type="stringValue", is_link=False):
        return color_cell(value, self.COLORS[self.result], type=type, is_link=is_link)

    def sheets_row(self):
        link_and_name = [
            self.sheets_cell(self.format_url(), is_link=True),
            self.sheets_cell(self.program_name),
            self.sheets_cell(self.result.value),
        ]

        if self.result == Result.SKIPPED:
            return wrap_row(link_and_name + [self.sheets_cell("")] * 4)

        return wrap_row(
            link_and_name
            + [
                self.sheets_cell(self.expected_value, "numberValue"),
                self.sheets_cell(self.value, "numberValue"),
                self.sheets_cell(self.expected_eligibility, "boolValue"),
                self.sheets_cell(self.eligibility, "boolValue"),
            ]
        )


class ValidationResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results: list[ValidationResult] = []

    def skip(self, uuid: str, program_name: str):
        self.skipped += 1
        self.results.append(ValidationResult(uuid, program_name, Result.SKIPPED))

    def test(
        self,
        uuid: str,
        program_id: int,
        program_name: str,
        expected_value: int,
        value: int,
        expected_eligibility: bool,
        eligibility: bool,
    ):
        if expected_value == value and expected_eligibility == eligibility:
            self.passed += 1
            result = Result.PASSED
        else:
            self.failed += 1
            result = Result.FAILED

        self.results.append(
            ValidationResult(
                uuid,
                program_name,
                result,
                program_id,
                expected_value,
                value,
                expected_eligibility,
                eligibility,
            )
        )


class Command(BaseCommand):
    help = """
    Run current eligibility results, and compare to expected value and eligibility
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--program",
            help="Run tests for a specific program",
        )
        parser.add_argument(
            "--hide-skipped",
            action=argparse.BooleanOptionalAction,
            help="Don't display skipped validations",
        )
        parser.add_argument("-s", "--sheet-id", help="The Google sheet id to display results in")

    def handle(self, *args, **options):
        if options["program"] is not None:
            queryset = Validation.objects.filter(program_name=options["program"])
        else:
            queryset = Validation.objects.all()

        validations = queryset.prefetch_related("screen").order_by("-created_date")

        # group validations together based on screen
        grouped_validations: dict[int, list[Validation]] = {}
        for validation in validations:
            if validation.screen.id not in grouped_validations:
                grouped_validations[validation.screen.id] = []

            grouped_validations[validation.screen.id].append(validation)

        validation_results = ValidationResults()
        for group in grouped_validations.values():
            screen = group[0].screen
            results = eligibility_results(screen, batch=True)[0]

            for validation in group:
                program = self._find_program(validation, results)

                if program is None:
                    validation_results.skip(screen.uuid, validation.program_name)
                    continue

                validation_results.test(
                    screen.uuid,
                    program["program_id"],
                    validation.program_name,
                    int(validation.value),
                    program["estimated_value"],
                    validation.eligible,
                    program["eligible"],
                )
            self._stdout_display(validation_results, options["hide_skipped"])
            if options["sheet_id"] is not None:
                self._google_sheet_display(validation_results, options["sheet_id"], options["hide_skipped"])

    def _find_program(self, validation: Validation, programs):
        for program in programs:
            if program["external_name"] == validation.program_name:
                return program

    def _stdout_display(self, results: ValidationResults, hide_skipped: bool):
        for result in results.results:
            url_and_name = f"{result.format_url()} {result.program_name}"
            text = f"{url_and_name} {result.format_value_change()}"
            if result.result == Result.PASSED:
                self.stdout.write(self.style.SUCCESS(text))
            if result.result == Result.FAILED:
                self.stdout.write(self.style.ERROR(text))
            if result.result == Result.SKIPPED and not hide_skipped:
                self.stdout.write(f"{url_and_name} Skipped")

        self.stdout.write(self.style.SUCCESS(f"\nPassed: {results.passed}"))
        self.stdout.write(self.style.ERROR(f"Failed: {results.failed}"))
        if not hide_skipped:
            self.stdout.write(f"Skipped: {results.skipped}")

    def _google_sheet_display(self, results: ValidationResults, google_sheet_id: str, hide_skipped: bool):
        column_count = 7
        row_data = [
            wrap_row(
                [
                    title_cell("URL"),
                    title_cell("Program Name"),
                    title_cell("Result"),
                    title_cell("Expected Value"),
                    title_cell("Actual Value"),
                    title_cell("Expected Eligibility"),
                    title_cell("Actual Eligibility"),
                ]
            )
        ]
        for result in results.results:
            row_data.append(result.sheets_row())

        sheet = GoogleSheets.sheet

        # there is around a 1 in 2 billion chance of a conflct, so if that happens,
        # buy a lottery ticket and run the script again.
        sheet_id = randint(1_000, 2_147_483_647)
        requests = [
            {  # add new sheet
                "addSheet": {
                    "properties": {
                        "sheetId": sheet_id,
                        "title": f"Results: {datetime.today().strftime('%Y/%m/%d %H:%M:%S')}",
                        "index": 0,
                    },
                }
            },
            {  # add data and format
                "updateCells": {
                    "rows": row_data,
                    "fields": "userEnteredFormat,userEnteredValue",
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "startColumnIndex": 0,
                        "endColumnIndex": column_count,
                    },
                },
            },
            {  # resize columns
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": column_count,
                    }
                }
            },
            {  # add filters
                "setBasicFilter": {
                    "filter": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "startColumnIndex": 0,
                            "endColumnIndex": column_count,
                        },
                        "sortSpecs": [
                            {
                                "dimensionIndex": 1,
                                "sortOrder": "ASCENDING",
                            }
                        ],
                        "criteria": (
                            {
                                2: {"hiddenValues": [Result.SKIPPED.value]},
                            }
                            if hide_skipped
                            else {}
                        ),
                    }
                }
            },
        ]
        body = {"requests": requests}
        try:
            sheet.batchUpdate(spreadsheetId=google_sheet_id, body=body).execute()
        except HttpError:
            self.stdout.write(
                self.style.ERROR("\nGoogle Sheet not found. Make sure that you share the sheet with the service acount")
            )
