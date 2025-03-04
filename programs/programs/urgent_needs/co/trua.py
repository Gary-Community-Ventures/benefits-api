from integrations.services.sheets.sheets import GoogleSheetsCache
from ..base import UrgentNeedFunction


# also in /programs/programs/urgent_needs/co/trua.py
class TruaIncomeLimits(GoogleSheetsCache):
    sheet_id = "1rF2vnqvfPFWVLLcImGZX417X36GRDhqFg-4fJBNr5p8"
    range_name = "current AMI!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "")) for a in data[0]]


class Trua(UrgentNeedFunction):
    dependencies = ["household_size", "income_amount", "income_frequency"]
    income_limits = TruaIncomeLimits()

    def eligible(self):
        """
        Return True if the household is below the income limit for their household size
        """
        household_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = self.income_limits.fetch()[self.screen.household_size - 1]
        has_rent_or_mortgage = self.screen.has_expense(["rent"])

        return household_income <= income_limit and has_rent_or_mortgage
