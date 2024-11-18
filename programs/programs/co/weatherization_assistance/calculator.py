from integrations.services.sheets.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_screen
from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class SmiCache(GoogleSheetsCache):
    sheet_id = "1KE0fBYqmIcwXO-tLu4RIF47GLFTyxLi4mi3uG-llMDY"
    range_name = "current 60% SMI!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "")) for a in data[0]]


class AmiCache(GoogleSheetsCache):
    sheet_id = "1KE0fBYqmIcwXO-tLu4RIF47GLFTyxLi4mi3uG-llMDY"
    range_name = "current 80% AMI!A2:I"
    default = {}

    def update(self):
        data = super().update()

        county_fpls = {r[0].strip() + " County": self._get_income_limits(r[1:]) for r in data}

        return county_fpls

    def _get_income_limits(self, raw_limits: list[str]):
        limits = []

        for limit in raw_limits:
            limits.append(int(limit.replace(",", "")))

        return limits


class WeatherizationAssistance(ProgramCalculator):
    smi_cache = SmiCache()
    ami_cache = AmiCache()
    presumptive_eligibility = ("andcs", "ssi", "snap", "leap", "tanf")
    amount = 350
    dependencies = ["household_size", "income_amount", "income_frequency"]

    def household_eligible(self, e: Eligibility):
        # income condition
        income_limit = self.smi_cache.fetch()[self.screen.household_size - 1]
        if self.screen.zipcode != None:
            counties = counties_from_screen(self.screen)

            for county in counties:
                ami_limit = self.ami_cache.fetch()[county][self.screen.household_size - 1]

                if ami_limit > income_limit:
                    income_limit = ami_limit

        income = int(self.screen.calc_gross_income("yearly", ["all"]))
        income_eligible = income <= income_limit

        # categorical eligibility
        categorical_eligible = False
        for program in WeatherizationAssistance.presumptive_eligibility:
            if self.screen.has_benefit(program):
                categorical_eligible = True
                break
        e.condition(income_eligible or categorical_eligible, messages.income(income, income_limit))

        # rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        e.condition(has_rent_or_mortgage)
