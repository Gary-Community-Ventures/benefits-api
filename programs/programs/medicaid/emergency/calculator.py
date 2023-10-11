import programs.programs.messages as messages


def calculate_emergency_medicaid(screen, data, program):
    emergency_medicaid = EmergencyMedicaid(screen, data)
    eligibility = emergency_medicaid.eligibility
    value = emergency_medicaid.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class EmergencyMedicaid():
    amount = 9_540

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
        # Does qualify for Medicaid
        is_medicaid_eligible = self.screen.has_types_of_insurance(['medicaid'])
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break
        self._condition(is_medicaid_eligible, messages.must_have_benefit('Medicaid'))

        # Household member is pregnant
        is_pregnant = False
        for member in self.screen.household_members.all():
            if member.pregnant:
                is_pregnant = True
        self._condition(is_pregnant, messages.is_pregnant())

    def calc_value(self):
        self.value = EmergencyMedicaid.amount

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
