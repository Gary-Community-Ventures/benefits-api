from integrations.services.sheets.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_screen
from programs.programs.calc import Eligibility, ProgramCalculator


class EnergyOutreachSolarIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"  # same sheet as Energy Outreach Colorado
    range_name = "'current'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class EnergyOutreachSolar(ProgramCalculator):
    amount = 1
    dependencies = ["household_size", "energy_calculator", "income_amount", "income_frequency"]
    electricity_providers = ["co-black-hills-energy", "co-xcel-energy"]
    income_limits = EnergyOutreachSolarIncomeLimitCache()

    def household_eligible(self, e: Eligibility):
        # income
        income = self.screen.calc_gross_income("yearly", ["all"])
        county = counties_from_screen(self.screen)[0]
        income_limit = self.income_limits.fetch()[county][self.screen.household_size]
        e.condition(income < income_limit)

        # utility providers
        e.condition(self.screen.energy_calculator.has_electricity_provider(self.electricity_providers))
