from integrations.services.sheets.sheets import GoogleSheetsCache
from integrations.util.cache import Cache
from integrations.services.sheets import GoogleSheets
from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_zip
import math


class LeapValueCache(Cache):
    expire_time = 60 * 60 * 24
    default = []
    sheet_id = "1W8WbJsb5Mgb4CUkte2SCuDnqigqkmaO3LC0KSfhEdGg"
    range_name = "'FFY 2024'!A1:G65"
    county_column = "2023/2024 Season\nUpdated: \n4/30/2024"
    average_column = "Average Benefit"

    def update(self):
        data = GoogleSheets(self.sheet_id, self.range_name).data_by_column(self.county_column, self.average_column)

        return [[row[self.county_column], row[self.average_column]] for row in data if row != []]


class LeapIncomeLimitCache(GoogleSheetsCache):
    sheet_id = "15dxjTY0k1l4nqm8TAwtJPaMpYWPDbwTYKGbDu7Dc3bI"
    range_name = "current!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "")) for a in data[0]]


class EnergyAssistance(ProgramCalculator):
    dependencies = ["income_frequency", "income_amount", "zipcode", "household_size"]
    county_values = LeapValueCache()
    income_bands = LeapIncomeLimitCache()  # monthly

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # income
        frequency = "monthly"
        income_types = ["all"]
        income_limit = EnergyAssistance.income_bands.fetch()[self.screen.household_size - 1]
        leap_income = self.screen.calc_gross_income(frequency, income_types)

        e.condition(leap_income <= income_limit, messages.income(leap_income, income_limit))

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        e.condition(has_rent_or_mortgage)

        return e

    def value(self, eligible_members: int):
        data = self.county_values.fetch()

        # if there is no county, then we want to estimate based off of zipcode
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        values = []
        for row in data:
            county = row[0].strip().replace("Application County: ", "") + " County"
            if county in counties:
                values.append(int(float(row[1].replace("$", ""))))

        value = 362
        lowest = math.inf

        # get lowest value from zipcodes
        for possible_value in values:
            if possible_value < lowest:
                value = possible_value
                lowest = possible_value

        return value
