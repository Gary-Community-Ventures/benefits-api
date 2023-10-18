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
    fpl_percent = 2.6

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
        is_medicaid_eligible = self.screen.has_benefit('medicaid')
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"] or is_medicaid_eligible
                break

        self._condition(
            not is_medicaid_eligible,
            messages.must_not_have_benefit('Medicaid')
        )

        # Income
        income_limit = int(FamilyPlanningServices.fpl_percent * self.fpl[self.screen.household_size] / 12)
        gross_income = int(self.screen.calc_gross_income('monthly', ['all']))

        self._condition(
            gross_income < income_limit,
            messages.income(gross_income, income_limit)
        )

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
