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
        # Has a disability
        someone_is_blind = False
        someone_is_disabled = False
        for member in self.screen.household_members.all():
            someone_is_blind = someone_is_blind or member.visually_impaired
            someone_is_disabled = someone_is_disabled or member.disabled

        self._condition(someone_is_blind or someone_is_disabled, messages.has_disability())

        # Income test
        income_limit = Ssdi.income_limit_blind if someone_is_blind else Ssdi.income_limit
        household_income = self.screen.calc_gross_income('yearly', ('all',))
        self._condition(household_income < income_limit, messages.income(household_income, income_limit))

    def calc_value(self):
        self.value = Ssdi.amount * 12

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
