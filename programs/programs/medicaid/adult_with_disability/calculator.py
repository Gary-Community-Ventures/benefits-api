import programs.programs.messages as messages


def calculate_medicaid_adult_with_disability(screen, data, program):
    awd = MedicaidAdultWithDisability(screen, data, program)
    eligibility = awd.eligibility
    value = awd.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class MedicaidAdultWithDisability():
    min_age = 16
    max_income_percent = 4.5
    earned_deduction = 65
    earned_percent = .5
    amount = 310
    unearned_deduction = 20

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
        is_medicaid_eligible = self.screen.has_insurance_types(('medicaid',))
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break
        self._condition(not is_medicaid_eligible, messages.must_not_have_benefit('Medicaid'))

        def income_eligible(member):
            income_limit = self.fpl[self.screen.household_size] * MedicaidAdultWithDisability.max_income_percent
            earned_deduction = MedicaidAdultWithDisability.earned_deduction
            earned_percent = MedicaidAdultWithDisability.earned_percent
            earned = max(0, int(
                (int(member.calc_gross_income('yearly', ['earned'])) - earned_deduction) * earned_percent
            ))
            unearned_deduction = MedicaidAdultWithDisability.unearned_deduction
            unearned = int(member.calc_gross_income('yearly', ['unearned'])) - unearned_deduction
            return earned + unearned <= income_limit

        self.eligible_members = self._member_eligibility(self.screen.household_members.all(), [
            (lambda m: m.age >= MedicaidAdultWithDisability.min_age, messages.older_than(min_age=16)),
            (lambda m: m.disabled or m.visually_impaired, messages.has_disability()),
            (lambda m: m.insurance.has_insurance_types(('employer', 'private', 'none', 'dont_know')), None),
            (income_eligible, None)
        ])

    def calc_value(self):
        self.value = MedicaidAdultWithDisability.amount * len(self.eligible_members) * 12

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
        elif len(eligible_members) <= 0:
            self.eligibility['eligible'] = False

        return self._member_eligibility(eligible_members, conditions)
