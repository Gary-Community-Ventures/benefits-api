from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.sheets import sheets_get_data
from integrations.util import Cache


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
    dependencies = ['income_frequency', 'income_amount', 'county', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # income
        frequency = "monthly"
        income_types = ['all']
        income_limit = EnergyAssistance.income_bands[self.screen.household_size]
        leap_income = self.screen.calc_gross_income(frequency, income_types)

        e.condition(leap_income < income_limit, messages.income(leap_income, income_limit))

        return e

    def value(self, eligible_members: int):
        value = 362
        data = cache.fetch()
        for row in data:
            county = row[0].replace('Application County: ', '') + 'County'
            if county == self.screen.county:
                value = int(float(row[1].replace('$', '')))

        return value


class LeapValueCache(Cache):
    expire_time = 60 * 60 * 24
    default = []

    def update(self):
        spreadsheet_id = '1W8WbJsb5Mgb4CUkte2SCuDnqigqkmaO3LC0KSfhEdGg'
        range_name = "'FFY 2024'!A2:F129"
        sheet_values = sheets_get_data(spreadsheet_id, range_name)

        if not sheet_values:
            raise Exception('Sheet unavailable')

        data = [[row[0], row[5]] for row in sheet_values if row != []]

        return data


cache = LeapValueCache()
