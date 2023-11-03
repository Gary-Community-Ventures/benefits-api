import programs.programs.messages as messages


def calculate_omnisalud(screen, data, program):
    omnisalud = OmniSalud(screen)
    eligibility = omnisalud.eligibility
    value = omnisalud.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class OmniSalud():
    individual_limit = 1699
    family_4_limit = 3469
    amount = {'adult': 310, 'child': 200, 'senior': 170}

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
        # Income test
        gross_income = self.screen.calc_gross_income("monthly", ["all"])
        income_band = OmniSalud.family_4_limit if self.screen.household_size >= 4 else OmniSalud.individual_limit
        self._condition(gross_income <= income_band, messages.income(gross_income, income_band))

        # No health insurance
        has_no_hi = self.screen.has_insurance_types(('none',))
        self._condition(has_no_hi, messages.has_no_insurance())

    def calc_value(self):
        child_value = OmniSalud.amount['child'] * self.screen.num_children()
        num_seniors = self.screen.num_adults(age_max=65)
        senior_value = OmniSalud.amount['senior'] * num_seniors
        adult_value = OmniSalud.amount['adult'] * (self.screen.num_adults() - num_seniors)

        self.value = (child_value + adult_value + senior_value) * 12

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
