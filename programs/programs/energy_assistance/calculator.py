from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.sheets import sheets_get_data
from integrations.util import Cache
from programs.co_county_zips import counties_from_zip
import math


class EnergyAssistance(ProgramCalculator):
    income_bands = {
        1: 3_081,
        2: 4_030,
        3: 4_978,
        4: 5_926,
        5: 6_875,
        6: 7_823,
        7: 8_001,
        8: 8_179,
    }
    dependencies = ['income_frequency', 'income_amount', 'zipcode', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # income
        frequency = "monthly"
        income_types = ['all']
        income_limit = EnergyAssistance.income_bands[self.screen.household_size]
        leap_income = self.screen.calc_gross_income(frequency, income_types)

        e.condition(
            leap_income < income_limit, messages.income(leap_income, income_limit)
        )

        return e

    def value(self, eligible_members: int):
        data = cache.fetch()

        # if there is no county, then we want to estimate based off of zipcode
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        values = []
        for row in data:
            county = row[0].strip().replace('Application County: ', '') + ' County'
            if county in counties:
                values.append(int(float(row[1].replace('$', ''))))

        value = 362
        lowest = math.inf

        # get lowest value from zipcodes
        for possible_value in values:
            if possible_value < lowest:
                value = possible_value
                lowest = possible_value

        return value


class LeapValueCache(Cache):
    expire_time = 60 * 60 * 24
    default = []

    def update(self):
        spreadsheet_id = '1W8WbJsb5Mgb4CUkte2SCuDnqigqkmaO3LC0KSfhEdGg'
        range_name = "'FFY 2024'!A2:F65"
        sheet_values = sheets_get_data(spreadsheet_id, range_name)

        if not sheet_values:
            raise Exception('Sheet unavailable')

        data = [[row[0], row[5]] for row in sheet_values if row != []]

        return data


cache = LeapValueCache()
