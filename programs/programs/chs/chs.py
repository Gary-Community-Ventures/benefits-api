from django.conf import settings

def calculate_chs(screen, data):
    chs = Chs(screen)
    eligibility = chs.eligibility
    value = chs.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Chs():
    amount = 17200
    max_age = 5
    min_age = 3

    def __init__(self, screen):
        self.screen = screen

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

        self.calc_eligibility()

        self.calc_value()

    def calc_eligibility(self):
        #has young child
        num_children = self.screen.num_children(age_min=Chs.min_age, age_max=Chs.max_age)

        self._condition(num_children >= 1,
                        f"Must have a child between the ages of {Chs.min_age} and {Chs.max_age}")

        #income
        income_limit = int(settings.FPL2022[self.screen.household_size]/12)
        gross_income = int(self.screen.calc_gross_income('monthly', ['all']))

        self._condition(gross_income < income_limit,
                        f"Income of ${gross_income} must be less than ${income_limit}")

    def calc_value(self):
        self.value = Chs.amount

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
