from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
import math


class LowWageCovidRelief(ProgramCalculator):
    amount = 1_500
    auto_eligible_benefits = ('medicaid', 'tanf', 'snap', 'wic', 'leap')
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
    county = 'Adams County'
    dependencies = ['county', 'household_size', 'income_amount', 'income_frequency']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # lives in Adams County
        in_adams_county = self.screen.county == LowWageCovidRelief.county
        e.condition(in_adams_county, messages.location())

        # other benefits
        for benefit in LowWageCovidRelief.auto_eligible_benefits:
            has_benefit = self.screen.has_benefit(benefit)

        for benefit in self.data:
            if benefit['name_abbreviated'] in LowWageCovidRelief.auto_eligible_benefits and benefit['eligible']:
                has_benefit = True
                break

        # meets income limit
        income_limit = LowWageCovidRelief.income_limits[self.screen.household_size]
        income = self.screen.calc_gross_income('monthly', ['all'])
        meets_income_limit = income <= income_limit

        if not (meets_income_limit or has_benefit):
            e.eligible = False

        return e

    def value(self):
        return LowWageCovidRelief.amount
