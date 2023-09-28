import programs.programs.messages as messages


def calculate_medicaid_child_with_disability(screen, data, program):
    cwd = ChildWithDisability(screen, data)
    eligibility = cwd.eligibility
    value = cwd.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class ChildWithDisability():
    max_age = 18

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
        # Does not qualify for Medicaid
        is_medicaid_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break
        self._condition(not is_medicaid_eligible, messages.must_not_have_benefit('Medicaid'))

        # max_income = 0

        self._member_eligibility(self.screen.household_members.all(), (
            (lambda m: m.age <= ChildWithDisability.max_age, messages.child()),
            (lambda m: m.disabled or m.visually_impaired, messages.has_disability())
        ))

    def calc_value(self):
        value = 0
        self.value = value

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

    def _member_eligibility(self, members, conditions):
        '''
        Filter out members that do not meet the condition and make eligibility messages
        '''
        if len(conditions) <= 0:
            return members

        [condition, message] = conditions.pop()
        eligible_members = filter(condition, members)
        self._condition(len(eligible_members), message)

        self._member_eligibility(eligible_members, conditions)
