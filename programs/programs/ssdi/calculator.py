import programs.programs.messages as messages


def calculate_ssdi(screen, data, program):
    rhc = Ssdi(screen)
    eligibility = rhc.eligibility
    value = rhc.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Ssdi():
    amount = 1_364
    income_limit = 1_470
    income_limit_blind = 2_460

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
        someone_is_disabled = False
        someone_meets_income_test = False
        lowest_income = float('inf')
        self.members_eligible = 0
        for member in self.screen.household_members.all():
            member_is_disabled = member.disabled or member.visually_impaired
            someone_is_disabled = someone_is_disabled or member_is_disabled

            income_limit = Ssdi.income_limit_blind if member.visually_impaired else Ssdi.income_limit
            member_income = member.calc_gross_income('monthly', ('all',))
            member_meets_income_test = (member_income < income_limit) and member_is_disabled
            someone_meets_income_test = someone_meets_income_test or member_meets_income_test
            if member_meets_income_test and member_is_disabled:
                self.members_eligible += 1
            if member_income < lowest_income and member_is_disabled:
                lowest_income = member_income

        # Has a disability
        self._condition(someone_is_disabled, messages.has_disability())

        # Income test
        self._condition(someone_meets_income_test, messages.income(lowest_income, income_limit))

    def calc_value(self):
        self.value = Ssdi.amount * 12 * self.members_eligible

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
