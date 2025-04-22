from integrations.services.sheets.sheets import GoogleSheetsCache
from screener.models import Screen


class Ami(GoogleSheetsCache):
    sheet_id = "1ZnOg_IuT7TYz2HeF31k_FSPcA-nraaMG3RUWJFUIIb8"
    range_name = "current!A2:N"
    default = {}

    YEAR_INDEX = 0
    STATE_INDEX = 1
    COUNTY_INDEX = 2
    HOUSEHOLD_SIZE_START_INDEX = 6
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
            for i in range(self.HOUSEHOLD_SIZE_START_INDEX, self.MAX_HOUSEHOLD_SIZE + self.HOUSEHOLD_SIZE_START_INDEX):
                try:
                    # handle rows with errors
                    value = int(row[i])
                except ValueError:
                    continue_outer = True
                    break

                values[i - self.HOUSEHOLD_SIZE_START_INDEX + 1] = value

            if continue_outer:
                continue

            if year not in ami:
                ami[year] = {}
            if state not in ami[year]:
                ami[year][state] = {}

            ami[year][state][county] = values

        return ami

    def get_screen_ami(self, screen: Screen, year: int):
        data = self.fetch()

        return data[year][screen.white_label][screen.county][screen.household_size]


ami = Ami()
