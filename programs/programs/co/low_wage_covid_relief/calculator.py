from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.helpers import STATE_MEDICAID_OPTIONS
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_zip
import math


class LowWageCovidRelief(ProgramCalculator):
    amount = 1_500
    auto_eligible_benefits = (*STATE_MEDICAID_OPTIONS, "tanf", "snap", "wic", "leap")
    income_limits = {
        1: -math.inf,
        2: 3_266.25,
        3: 4_117.50,
        4: 4_968.75,
        5: 5_820.00,
        6: 6_671.25,
        7: 7_522.50,
        8: 8_373.75,
    }
    county = "Adams County"
    dependencies = ["zipode", "household_size", "income_amount", "income_frequency"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # lives in Adams County
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        in_adams_county = LowWageCovidRelief.county in counties
        e.condition(in_adams_county, messages.location())

        # other benefits
        for benefit in LowWageCovidRelief.auto_eligible_benefits:
            has_benefit = self.screen.has_benefit(benefit)

        for benefit in self.data:
            if benefit["name_abbreviated"] in LowWageCovidRelief.auto_eligible_benefits and benefit["eligible"]:
                has_benefit = True
                break

        # meets income limit
        income_limit = LowWageCovidRelief.income_limits[self.screen.household_size]
        income = self.screen.calc_gross_income("monthly", ["all"])
        meets_income_limit = income <= income_limit

        if not (meets_income_limit or has_benefit):
            e.eligible = False

        return e
