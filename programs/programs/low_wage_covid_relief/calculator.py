import programs.programs.messages as messages
import math


def calculate_low_wage_covid_relief(screen, data, program):
    lwcr = LowWageCovidRelief(screen, data)
    eligibility = lwcr.eligibility
    value = lwcr.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class LowWageCovidRelief():
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

    def __init__(self, screen, data):
        self.screen = screen
        self.data = data

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

        self.calc_eligibility()

        self.calc_value()

    def calc_eligibility(self):
        # lives in Adams County
        in_adams_county = self.screen.county == 'Adams County'
        self._condition(in_adams_county, messages.location())

        # other benefits
        has_benefit = self.screen.has_benefit(LowWageCovidRelief.auto_eligible_benefits)
        for benefit in self.data:
            if benefit['name_abbreviated'] in LowWageCovidRelief.auto_eligible_benefits and benefit['eligible']:
                has_benefit = True
                break

        # meets income limit
        income_limit = LowWageCovidRelief.income_limits[self.screen.household_size]
        income = self.screen.calc_gross_income('monthly', ['all'])
        meets_income_limit = income < income_limit

        if not (meets_income_limit or has_benefit):
            self.eligibility['eligible'] = False

    def calc_value(self):
        self.value = LowWageCovidRelief.amount

    def _failed(self, msg):
        self.eligibility["eligible"] = False
        self.eligibility["failed"].append(msg)

    def _passed(self, msg):
        self.eligibility["passed"].append(msg)

    def _condition(self, condition, msg):
        if condition is True:
            self._passed(msg)
        else:
            self._failed(msg)
