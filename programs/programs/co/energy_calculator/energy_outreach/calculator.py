from integrations.services.income_limits import ami
from programs.programs.calc import Eligibility, ProgramCalculator


class EnergyCalculatorEnergyOutreach(ProgramCalculator):
    ami_percent = "80%"
    amount = 1
    dependencies = ["energy_calculator", "income_frequency", "income_amount", "household_size", "county"]

    def household_eligible(self, e: Eligibility):
        # income
        income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = ami.get_screen_ami(self.screen, self.ami_percent, self.program.year.period)
        e.condition(income <= income_limit)

        # past due heating
        e.condition(
            self.screen.energy_calculator.electricity_is_disconnected
            or self.screen.energy_calculator.has_past_due_energy_bills
        )
