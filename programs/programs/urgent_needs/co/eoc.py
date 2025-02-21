from ..base import UrgentNeedFunction
from integrations.services.sheets import GoogleSheetsCache


class EocIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"
    range_name = "'current'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class Eoc(UrgentNeedFunction):
    dependencies = ["income_amount", "income_frequency", "household_size", "county"]
    limits_cache = EocIncomeLimitCache()

    def eligible(self):
        """
        Return True if the household is below the income limit for their county and household size
        """

        income = int(self.screen.calc_gross_income("yearly", ["all"]))

        limits = Eoc.limits_cache.fetch()

        if self.screen.county not in limits:
            return False

        income_limit = limits[self.screen.county][self.screen.household_size - 1]

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])

        return income < income_limit and has_rent_or_mortgage
