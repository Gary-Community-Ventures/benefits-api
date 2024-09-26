from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages
from integrations.services.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_screen


class EmergencyRentalAssistanceIncomeLimitsCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1QHb-ZT0Y2oWjFMoeP_wy8ClveslINWdehb-CXhB8WSE"
    range_name = "'2022 80% AMI'!A2:I"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class EmergencyRentalAssistance(ProgramCalculator):
    amount = 13_848
    expenses = ["rent"]
    dependencies = ["income_amount", "income_frequency", "household_size", "zipcode"]
    income_cache = EmergencyRentalAssistanceIncomeLimitsCache()

    def household_eligible(self, e: Eligibility):
        # Income test
        income_limits = EmergencyRentalAssistance.income_cache.fetch()

        counties = counties_from_screen(self.screen)
        county_name = counties[0]
        for county in counties:
            if county in income_limits:
                county_name = county
                break

        income = self.screen.calc_gross_income("yearly", ["all"])
        # NOTE: 80% to income is already applied in the sheet.
        income_limit = income_limits[county_name][self.screen.household_size - 1]
        e.condition(income < income_limit, messages.income(income, income_limit))

        # has rent expense
        has_rent = self.screen.has_expense(EmergencyRentalAssistance.expenses)
        e.condition(has_rent)
