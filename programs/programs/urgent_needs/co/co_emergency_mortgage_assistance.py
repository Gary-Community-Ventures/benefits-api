from ..base import UrgentNeedFunction
from integrations.services.sheets import GoogleSheetsCache


class CoEmergencyMortgageIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1M_BQxs135UV4uO-CUpHtt9Xy89l1RmSufdP9c3nEh-M"
    range_name = "'100% AMI 2023'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0] + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class CoEmergencyMortgageAssistance(UrgentNeedFunction):
    limits_cache = CoEmergencyMortgageIncomeLimitCache()
    dependencies = ["income_amount", "income_frequency", "household_size", "county"]

    def eligible(self):
        income = int(self.screen.calc_gross_income("yearly", ["all"]))

        limits = CoEmergencyMortgageAssistance.limits_cache.fetch()

        if self.screen.county not in limits:
            return False

        income_limit = limits[self.screen.county][self.screen.household_size - 1]
        has_mortgage = self.screen.has_expense(["mortgage"])

        return income < income_limit and has_mortgage
