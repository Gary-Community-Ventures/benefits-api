from django.conf import settings
import programs.programs.messages as messages


def calculate_every_day_eats(screen, data, program):
    ede = EveryDayEats(screen, program)
    eligibility = ede.eligibility
    value = ede.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class EveryDayEats():
    amount = 600
    min_age = 60

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
        # Someone older that 60
        num_seniors = self.screen.num_adults(age_max=EveryDayEats.min_age)
        self._condition(num_seniors >= 1,
                        messages.older_than(EveryDayEats.min_age))

        # Income
        income_limit = 1.3 * self.fpl[self.screen.household_size]
        gross_income = self.screen.calc_gross_income('yearly', ['all'])

        self._condition(gross_income < income_limit,
                        messages.income(gross_income, income_limit))

    def calc_value(self):
        self.value = EveryDayEats.amount

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
