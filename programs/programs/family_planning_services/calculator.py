from django.conf import settings
import programs.programs.messages as messages


def calculate_family_planning_services(screen, data, program):
    fps = FamilyPlanningServices(screen, data, program)
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

    def __init__(self, screen, data, program):
        self.screen = screen
        self.data = data
        self.fpl = program.fpl.as_dict()

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

        self._condition(not (self.screen.has_benefit('medicaid') or is_medicaid_eligible),
                        messages.must_not_have_benefit('Medicaid'))

        # Child or Pregnant
        eligible_children = self.screen.num_children(age_max=FamilyPlanningServices.child_max_age,
                                                     include_pregnant=True)
        self._condition(eligible_children >= 1,
                        messages.child(0, FamilyPlanningServices.child_max_age))

        # Income
        income_limit = int(2.6 * self.fpl[self.screen.household_size]/12)
        income_types = ["wages", "selfEmployment"]
        gross_income = int(self.screen.calc_gross_income('monthly', income_types))

        self._condition(gross_income < income_limit,
                        messages.income(gross_income, income_limit))

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
