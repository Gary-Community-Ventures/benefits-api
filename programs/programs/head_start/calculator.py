from django.conf import settings
import programs.programs.messages as messages
from programs.programs.head_start.eligible_zipcodes import eligible_zipcode


def calculate_head_start(screen, data, program):
    chs = HeadStart(screen, program)
    eligibility = chs.eligibility
    value = chs.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class HeadStart():
    amount = 10655
    max_age = 5
    min_age = 3

    def __init__(self, screen, program):
        self.screen = screen
        self.fpl = program.fpl.as_dict()

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

        self.calc_eligibility()

        self.calc_value()

    def calc_eligibility(self):
        # has young child
        num_children = self.screen.num_children(age_min=HeadStart.min_age, age_max=HeadStart.max_age)

        self._condition(num_children >= 1,
                        messages.child(HeadStart.min_age, HeadStart.max_age))

        # income
        income_limit = int(self.fpl[self.screen.household_size]/12)
        gross_income = int(self.screen.calc_gross_income('monthly', ['all']))

        self._condition(gross_income < income_limit,
                        messages.income(gross_income, income_limit))

        # location
        self._condition(self.screen.county in eligible_zipcode,
                        messages.location())

    def calc_value(self):
        self.value = HeadStart.amount

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

    def _between(self, value, min_val, max_val):
        return min_val <= value <= max_val
