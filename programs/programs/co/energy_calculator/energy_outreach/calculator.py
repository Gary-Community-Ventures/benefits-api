from programs.co_county_zips import counties_from_screen
from programs.programs.calc import Eligibility, ProgramCalculator
from integrations.services.sheets.sheets import GoogleSheetsCache


class EnergyOutreachIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"  # same sheet as Energy Outreach Colorado
    range_name = "'current'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class EnergyCalculatorEnergyOutreach(ProgramCalculator):
    amount = 1
    income_limits = EnergyOutreachIncomeLimitCache()
    dependencies = ["energy_calculator", "income_frequency", "income_amount", "household_size"]

    def household_eligible(self, e: Eligibility):
        # income
        income = self.screen.calc_gross_income("yearly", ["all"])
        county = counties_from_screen(self.screen)[0]
        income_limit = self.income_limits.fetch()[county][self.screen.household_size]
        e.condition(income <= income_limit)

        # past due heating
        e.condition(
            self.screen.energy_calculator.electricity_is_disconnected
            or self.screen.energy_calculator.has_past_due_energy_bills
        )
