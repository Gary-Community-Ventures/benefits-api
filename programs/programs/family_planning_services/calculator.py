from django.conf import settings


def calculate_family_planning_services(screen, data):
    fps = FamilyPlanningServices(screen, data)
    eligibility = fps.eligibility
    value = fps.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class FamilyPlanningServices():
    amount = 404
    child_max_age = 18

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
        # Medicade eligibility
        is_medicaid_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break

        self._condition(not (self.screen.has_medicaid or is_medicaid_eligible),
                        "Must not be eligible for Medicaid")

        # Child or Pregnant
        eligible_children = self.screen.num_children(age_max=FamilyPlanningServices.child_max_age,
                                                     include_pregnant=True)
        self._condition(eligible_children >= 1,
                        f"Must have a child under the age of {FamilyPlanningServices.child_max_age} or have someone who is pregnant")

        # Income
        income_limit = int(2.6 * settings.FPL2022[self.screen.household_size]/12)
        income_types = ["wages", "selfEmployment"]
        gross_income = int(self.screen.calc_gross_income('monthly', income_types))

        self._condition(gross_income < income_limit,
                        f"Income of ${gross_income} must be less than ${income_limit}")

    def calc_value(self):
        self.value = FamilyPlanningServices.amount

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