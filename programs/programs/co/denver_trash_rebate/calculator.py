from programs.co_county_zips import counties_from_zip
from programs.programs.calc import ProgramCalculator, Eligibility
from integrations.services.sheets import GoogleSheetsCache
import programs.programs.messages as messages


class DenverAmiCache(GoogleSheetsCache):
    sheet_id = "1dahRu8UVdWBBU1jMiGiWehY4kOUkzcOmKRPJ-GfcfGo"
    range_name = "current Denver Trash - 60% AMI!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "")) for a in data[0]]


class DenverTrashRebate(ProgramCalculator):
    amount = 252
    county = "Denver County"
    ami = DenverAmiCache()
    dependencies = ["zipcode", "income_amount", "income_frequency", "household_size"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # county
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)
        e.condition(DenverTrashRebate.county in counties, messages.location())

        # income
        ami = DenverTrashRebate.ami.fetch()
        limit = ami[self.screen.household_size - 1]
        income = self.screen.calc_gross_income("yearly", ["all"])
        e.condition(income <= limit, messages.income(income, limit))

        # has rent or mortgage expense
        has_mortgage = self.screen.has_expense(["mortgage"])
        has_rent = self.screen.has_expense(["rent"])
        e.condition(has_mortgage or has_rent)

        return e
