def calculate_rhc(screen, data):
    rhc = Rhc(screen, data)
    eligibility = rhc.eligibility
    value = rhc.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Rhc():
    amount = 268

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
        #No health insurance
        has_no_hi = self.screen.has_types_of_hi(['none'])
        self._condition(has_no_hi,
                        "Someone in the household must not have health insurance")

        # Medicade eligibility
        is_medicaid_eligible = False
        for benefit in self.data:
            if benifit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligibile = benifit["eligible"]
                break

        self._condition(is_medicaid_eligibile,
                        "Must be eligible for Medicaid")

    def calc_value(self):
        self.value = Rhc.amount

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

