
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

        self.calc_value()

        self.calc_eligibility()

    def calc_eligibility(self):

        #No SSI
        self._condition(not self.screen.has_ssi,
                        "Must not be receiving SSI",
                        "Does not receive SSI")

        # No TANIF
        self._condition(not self.screen.has_tanf,
                        "Must not be eligible for TANF",
                        "Is not eligible for TANF")

        # Has disability/blindness
        member_has_blindness = False
        member_has_disability = False
        posible_eligble_members = []

        for member in self.screen.household_members.all():
            if member.disabled:
                member_has_disability = True
                posible_eligble_members.append(member)
            if member.visually_impaired:
                member_has_blindness = True
                posible_eligble_members.append(member)
        self._condition(member_has_blindness or member_has_disability,
                        "No one in the household has a disability or blindness",
                        "Someone in the household has a disability or blindness")

        # Right age
        min_age = 0 if member_has_blindness else 18

        for member in posible_eligble_members:
            is_in_age_range = self._between(member.age, min_age, 59)
            if not is_in_age_range:
                posible_eligble_members.remove(member)
        self._condition(len(posible_eligble_members) >= 0, 
                        "No member of the household with a disability is between the ages of 18-59 (0-59 for blindness)",
                        "A member of the house hold is with a disability is between the ages of 18-59 (0-59 for blindness)")

        # Meets income qualifications

    def calc_value(self):
        earned_income = self.screen
        self.actual_value = 0
        self.value = max(0, self.actual_value)

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

    def _between(self, value, min_val, max_val):
        return min_val <= value <= max_val