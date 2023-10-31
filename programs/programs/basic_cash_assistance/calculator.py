import programs.programs.messages as messages


def calculate_basic_cash_assistance(screen, data, program):
    bca = BasicCashAssistance(screen)
    eligibility = bca.eligibility
    value = bca.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class BasicCashAssistance():
    amount = 1_000

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
        # Lives in Denver
        in_denver = self.screen.county == 'Denver County'
        self._condition(in_denver, messages.location())

        # Has a child
        num_children = self.screen.num_children()
        self._condition(num_children >= 1, messages.child())

    def calc_value(self):
        self.value = BasicCashAssistance.amount

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
