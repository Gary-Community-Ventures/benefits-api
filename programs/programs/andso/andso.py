
def calculate_andso(screen, data):
    andso = Andso(screen)
    eligibility = andso.eligibility
    value = andso.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation

class Andso():
    def __init__(self, screen):
        self.screen = screen

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

    def calc_eligibility(self):

        #No SSI
        self._condition(not self.screen.has_ssi,
                        "Must not be receiving SSI",
                        "Does not receive SSI")

        # No TANIF
        self._condition(not self.screen.has_tanf,
                        "Must not be eligible for TANF",
                        "Is not eligible for TANF")

        # Right age

        # Has disability/blindness

        # Meets income qualifications

    def calc_value(self):
        self.value = 0
    
        self.calc_eligibility()

        self.calc_value()

    def _failed(self, msg):
        self.eligibility["eligible"] = False
        self.eligibility["failed"].append(msg)

    def _passed(self, msg):
        self.eligibility["passed"].append(msg)

    def _condition(self, condition, failed_msg, pass_msg):
        if condition is True:
            self._passed(pass_msg)
        else:
            self._failed(failed_msg)
