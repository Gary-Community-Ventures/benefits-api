from django.conf import settings

def calculate_fps(screen, data):
    fps = Fps(screen)
    eligibility = fps.eligibility
    value = fps.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Fps():
    amount = 404
    child_max_age = 18

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
        #Medicade eligibility
        #TODO: check if they are eligible for Medicare
        self._condition(self.screen.has_medicaid is True,
                        "Must not be eligible for Medicaid")

        #Child or Pregnant
        eligible_children = self.screen.num_children(age_max=Fps.child_max_age,
                                                include_pregnant=True)
        self._condition(eligible_children >= 1,
                        f"Must have a child under the age of {Fps.child_max_age} or have someone who is pregnant")

        #Income
        income_limit = 2.6 * settings.FPL2022[self.screen.household_size]
        income_types = ["wages", "selfEmployment"]
        gross_income = self.screen.calc_gross_income('yearly', income_types)

        self._condition(gross_income < income_limit,
                        f"Income of {gross_income} must be less than {income_limit}")

    def calc_value(self):
        self.value = Fps.amount

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
