def calculate_trua(screen, data):
    trua = Trua(screen)
    eligibility = trua.eligibility
    value = trua.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class Trua():
    average_amount = 5568 + 382.83 + 235.68
    income_bands = {
        1: 65680,
        2: 75040,
        3: 84400,
        4: 93760,
        5: 101280,
        6: 108800,
        7: 116320,
        8: 123840
    }

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
        income_band = Trua.income_bands[self.screen.household_size]
        self._condition(gross_income <= income_band,
                        f"Household makes ${gross_income} per month which must be less than ${income_band}")

    def calc_value(self):
        self.value = Trua.average_amount

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

