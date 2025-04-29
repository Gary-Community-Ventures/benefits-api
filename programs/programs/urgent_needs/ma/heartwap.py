from integrations.services.income_limits import smi
from ..base import UrgentNeedFunction


class Heartwap(UrgentNeedFunction):
    dependencies = ["income_amount", "income_frequency", "household_size"]
    max_income_percent = 0.6

    def eligible(self):
        # income
        income_limit = smi.get_screen_smi(self.screen, self.urgent_need.year.period) * self.max_income_percent
        income = self.screen.calc_gross_income("yearly", ["all"])

        return income <= income_limit
