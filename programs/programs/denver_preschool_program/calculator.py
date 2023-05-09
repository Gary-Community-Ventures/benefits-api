import programs.programs.messages as messages


def calculate_denver_preschool_program(screen, data, program):
    dpp = DenverPreschoolProgram(screen)
    eligibility = dpp.eligibility
    value = dpp.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class DenverPreschoolProgram():
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
        # Has a preschool child
        num_children = self.screen.num_children(age_min=DenverPreschoolProgram.min_age, age_max=DenverPreschoolProgram.max_age)

        self._condition(num_children >= 1,
                        messages.child(DenverPreschoolProgram.min_age,
                                       DenverPreschoolProgram.max_age))

        # Lives in Denver
        location = self.screen.county

        self._condition(location == "Denver County",
                        messages.location())

    def calc_value(self):
        self.value = DenverPreschoolProgram.amount

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
