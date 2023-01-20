
def calculate_dpp(screen, data):
    dpp = Dpp(screen)
    eligibility = dpp.eligibility
    value = dpp.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Dpp():
    amount = 788 * 12
    min_age = 3
    max_age = 4

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
        #Has a preschool child
        num_children = self.screen.num_children(age_min=Dpp.min_age, age_max=Dpp.max_age)

        self._condition(num_children >= 1,
                        f"Must have a child between the ages of {Dpp.min_age} and {Dpp.max_age}")

        #Lives in Denver
        location = self.screen.county

        self._condition(location == "Denver County",
                        "Must live in Denver")

    def calc_value(self):
        self.value = Dpp.amount

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
