from typing import Literal, Union
from integrations.services.sheets.sheets import GoogleSheetsCache
from screener.models import Screen


class Ami(GoogleSheetsCache):
    sheet_id = "1ZnOg_IuT7TYz2HeF31k_FSPcA-nraaMG3RUWJFUIIb8"
    range_name = "current!A2:BJ"
    default = {}

    YEAR_INDEX = 0
    STATE_INDEX = 1
    COUNTY_INDEX = 2
    LIMITS_START_INDEX = 6
    MAX_HOUSEHOLD_SIZE = 8

    def update(self):
        data = super().update()

        ami: dict[str, dict[str, dict[str, dict[int, int]]]] = {}

        for row in data:
            year = row[self.YEAR_INDEX]
            state = row[self.STATE_INDEX]
            county = row[self.COUNTY_INDEX]

            values = {}
            continue_outer = False
            percent = 80
            for j in range(self.LIMITS_START_INDEX, self.MAX_HOUSEHOLD_SIZE * 7, 8):
                income_limit_values = {}
                for i in range(j, self.MAX_HOUSEHOLD_SIZE + j):
                    try:
                        # handle rows with errors
                        value = int(float(row[i]))
                    except ValueError:
                        continue_outer = True
                        break

                    income_limit_values[i - j + 1] = value

                values[str(percent) + "%"] = income_limit_values
                percent -= 10

            if continue_outer:
                continue

            if year not in ami:
                ami[year] = {}
            if state not in ami[year]:
                ami[year][state] = {}

            ami[year][state][county] = values

        return ami

    def get_screen_ami(
        self,
        screen: Screen,
        percent: Union[
            Literal["80%"],
            Literal["70%"],
            Literal["60%"],
            Literal["50%"],
            Literal["40%"],
            Literal["30%"],
            Literal["20%"],
        ],
        year: int,
    ):
        data = self.fetch()

        return data[year][screen.white_label.state_code][screen.county][percent][screen.household_size]


ami = Ami()


class Smi(GoogleSheetsCache):
    sheet_id = "1kH--2b_VMY6lG_DXe2Xdhps3Flfi_ZIqc9oViWcxndE"
    range_name = "SMI!A2:J"
    default = {}

    YEAR_INDEX = 0
    STATE_INDEX = 1
    LIMITS_START_INDEX = 2

    def update(self):
        data = super().update()

        smi = {}
        for row in data:
            year = row[self.YEAR_INDEX]
            state = row[self.STATE_INDEX]

            limits = {}
            for i, limit in enumerate(row[self.LIMITS_START_INDEX :]):
                limits[i + 1] = int(float(limit))

            if year not in smi:
                smi[year] = {}

            smi[year][state] = limits

        return smi

    def get_screen_smi(self, screen: Screen, year: int):
        data = self.fetch()

        return data[year][screen.white_label.state]


smi = Smi()
