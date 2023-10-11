import programs.programs.messages as messages


def calculate_medicaid_child_with_disability(screen, data, program):
    cwd = MedicaidChildWithDisability(screen, data, program)
    eligibility = cwd.eligibility
    value = cwd.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class MedicaidChildWithDisability():
    max_age = 18
    max_income_percent = 3
    earned_deduction = 90
    income_percent = 1 - .33
    amount = 200

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
        # Does not qualify for Medicaid
        is_medicaid_eligible = self.screen.has_types_of_insurance(['medicaid'])
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break
        self._condition(not is_medicaid_eligible, messages.must_not_have_benefit('Medicaid'))

        income_limit = self.fpl[self.screen.household_size] * MedicaidChildWithDisability.max_income_percent
        earned = max(0, int(
            self.screen.calc_gross_income('yearly', ['earned']) - MedicaidChildWithDisability.earned_deduction
        ))
        unearned = self.screen.calc_gross_income('yearly', ['unearned'])
        income = (earned + unearned) * MedicaidChildWithDisability.income_percent
        self._condition(income <= income_limit, messages.income(income, income_limit))

        self.eligible_members = self._member_eligibility(self.screen.household_members.all(), [
            (lambda m: m.age <= MedicaidChildWithDisability.max_age, messages.child()),
            (lambda m: m.disabled or m.visually_impaired, messages.has_disability()),
            (lambda m: m.has_insurance_types(('employer', 'private', 'none', 'dont_know')), None),
            (lambda m: not (m.calc_gross_income('yearly', ['earned']) >= 0 and m.age >= 16), None),
        ])

    def calc_value(self):
        self.value = MedicaidChildWithDisability.amount * len(self.eligible_members) * 12

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
        eligible_members = list(filter(condition, members))
        if message:
            self._condition(len(eligible_members) >= 1, message)

        return self._member_eligibility(eligible_members, conditions)
