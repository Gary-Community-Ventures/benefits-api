
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

        self.calc_eligibility()

        self.calc_value()

    def _failed(self, msg):
        self.eligibility["eligible"] = False
        self.eligibility["failed"].append(msg)

    def _passed(self, msg):
        self.eligibility["passed"].append(msg)

    def calc_eligibility(self):

        #No SSI
        if self.screen.has_ssi:
            self._failed("Must not be receiving SSI")
        else:
            self._passed("Does not receive SSI")

        # No TANIF

        # Right age

        # Has disability/blindness

        # Meets income qualifications

    def calc_value(self):
        self.value = 0