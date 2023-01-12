from django.conf import settings

def calculate_cdhcs(screen, data):
    cdhcs = Cdhcs(screen)
    eligibility = cdhcs.eligibility
    value = cdhcs.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Cdhcs():
    amount = 80
    min_age = 60

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
        # Health insurance
        has_valid_hi = self.screen.has_types_of_hi(['none', 'employer', 'chp'])
        has_medicaid = self.screen.has_medicaid
        self._condition(has_valid_hi and not has_medicaid,
                        "Someone in the household must not have medicaid")

        # Age
        self._condition(self.screen.num_adults(age_max=Cdhcs.min_age)>=1,
                        f"Someone in the household must be {Cdhcs.min_age} or older")

        # Income test
        gross_income = self.screen.calc_gross_income("monthly", ["all"])
        income_band = int(2.5 * settings.FPL2022[self.screen.household_size]/12)
        self._condition(gross_income <= income_band,
                        f"Household makes ${gross_income} per month which must be less than ${income_band}")

    def calc_value(self):
        self.value = Cdhcs.amount * self.screen.num_adults(age_max=Cdhcs.min_age)

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
