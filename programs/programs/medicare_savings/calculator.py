import programs.programs.messages as messages


def calculate_medicare_savings(screen, data, program):
    medicare_savings = MedicareSavings(screen)
    eligibility = medicare_savings.eligibility
    value = medicare_savings.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class MedicareSavings():
    valid_insurance = ('none', 'employer', 'private', 'medicare')
    asset_limit = {
        'single': 10_590,
        'married': 16_630,
    }
    income_limit = {
        'single': 1_660,
        'married': 2239,
    }
    amount = 175

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
        members = self.screen.household_members.all()

        def asset_limit(member):
            status = 'married' if member.is_married()['is_married'] else 'single'
            return self.screen.household_assets < MedicareSavings.asset_limit[status]

        def income_limit(member):
            is_married = member.is_married()
            if not is_married['is_married']:
                status = 'single'
                spouse_income = 0
            else:
                status = 'married'
                spouse_income = is_married['married_to'].calc_gross_income('monthly', ('all',))
            max_income = MedicareSavings.income_limit[status]
            income = member.calc_gross_income('monthly', ('all',)) + spouse_income
            return income < max_income

        self.eligible_members = self._member_eligibility(
            members,
            [
                (lambda m: m.age >= 65, messages.older_than(65)),
                (
                    lambda m: m.insurance.has_insurance_types(MedicareSavings.valid_insurance),
                    messages.has_no_insurance()
                ),
                (asset_limit, None),
                (income_limit, None)
            ]
        )

    def calc_value(self):
        self.value = MedicareSavings.amount * len(self.eligible_members) * 12

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
