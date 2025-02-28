from integrations.services.sheets.sheets import GoogleSheetsCache
from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_screen


# also in /programs/programs/urgent_needs/co/trua.py
class TruaIncomeLimits(GoogleSheetsCache):
    sheet_id = "1rF2vnqvfPFWVLLcImGZX417X36GRDhqFg-4fJBNr5p8"
    range_name = "current AMI!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "")) for a in data[0]]


class Trua(ProgramCalculator):
    income_limits = TruaIncomeLimits()
    county = "Denver County"
    amount = 6_500
    dependencies = ["income_amount", "income_frequency", "household_size", "zipcode"]

    def household_eligible(self, e: Eligibility):
        # income
        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))
        income_limit = Trua.income_limits.fetch()[self.screen.household_size - 1]
        e.condition(gross_income <= income_limit, messages.income(gross_income, income_limit))

        # location
        counties = counties_from_screen(self.screen)
        e.condition(Trua.county in counties, messages.location())

        # rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        e.condition(has_rent_or_mortgage)
