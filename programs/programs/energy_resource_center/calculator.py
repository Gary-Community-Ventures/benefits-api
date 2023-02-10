def calculate_energy_resource_center(screen, data):
    erc = EnergyResourceCenter(screen)
    eligibility = erc.eligibility
    value = erc.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class EnergyResourceCenter():
    average_amount = 4000
    income_bands = {
        1: 2880,
        2: 3766,
        3: 4652,
        4: 5539,
        5: 6425,
        6: 7311,
        7: 7477,
        8: 7644
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
        income_band = EnergyResourceCenter.income_bands[self.screen.household_size]
        self._condition(gross_income <= income_band,
                        f"Household makes ${gross_income} per month which must be less than ${income_band}")

    def calc_value(self):
        self.value = EnergyResourceCenter.average_amount

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
