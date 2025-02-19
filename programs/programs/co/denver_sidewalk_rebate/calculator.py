from integrations.services.sheets.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_screen
from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class IncomeLimitsCache(GoogleSheetsCache):
    sheet_id = "1dahRu8UVdWBBU1jMiGiWehY4kOUkzcOmKRPJ-GfcfGo"
    range_name = "B2:I"
    default = {}

    def update(self):
        data = super().update()

        return self._format_amounts(data[0])

    @staticmethod
    def _format_amounts(amounts: list[str]):
        return [float(a.strip().replace(",", "")) for a in amounts]


class DenverSidewalkRebate(ProgramCalculator):
    county = "Denver County"
    income_limits = IncomeLimitsCache()
    presumptive_eligibility = ("co_medicaid", "snap", "tanf", "cccap")
    amount = 150
    dependencies = ["household_size", "income_amount", "income_frequency"]

    def household_eligible(self, e: Eligibility):
        # denver county condition
        screen_county = counties_from_screen(self.screen)
        e.condition(DenverSidewalkRebate.county in screen_county, messages.location())

        # income condition
        income_limit = DenverSidewalkRebate.income_limits.fetch()[self.screen.household_size - 1]

        income = int(self.screen.calc_gross_income("yearly", ["all"]))
        income_eligible = income <= income_limit

        # categorical eligibility
        categorical_eligible = False
        for program in DenverSidewalkRebate.presumptive_eligibility:
            if self.screen.has_benefit(program):
                categorical_eligible = True
                break

        e.condition(categorical_eligible or income_eligible, messages.income(income, income_limit))

        # mortgage expense
        e.condition(self._has_expense())

    def _has_expense(self):
        return self.screen.has_expense(["mortgage"])
