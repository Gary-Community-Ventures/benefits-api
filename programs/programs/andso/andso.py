from programs.programs.tanf.tanf import calculate_tanf

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

        self.calc_total_countable_income()

        self.calc_value()

    def calc_eligibility(self):

        #No SSI
        self._condition(not self.screen.has_ssi,
                        "Must not be receiving SSI",
                        "Does not receive SSI")

        # No TANIF
        tanf_eligible = calculate_tanf(self.screen)["eligibility"]["eligible"]
        self._condition(not (self.screen.has_tanf or tanf_eligible),
                        "Must not be eligible for TANF",
                        "Is not eligible for TANF")

        # Has disability/blindness
        member_has_blindness = False
        member_has_disability = False
        self.posible_eligble_members = []

        for member in self.screen.household_members.all():
            if member.disabled:
                member_has_disability = True
                self.posible_eligble_members.append(member)
            if member.visually_impaired:
                member_has_blindness = True
                self.posible_eligble_members.append(member)
        self._condition(member_has_blindness or member_has_disability,
                        "No one in the household has a disability or blindness",
                        "Someone in the household has a disability or blindness")

        # Right age
        min_age = 0 if member_has_blindness else 18

        for member in self.posible_eligble_members:
            is_in_age_range = self._between(member.age, min_age, 59)
            if not is_in_age_range:
                self.posible_eligble_members.remove(member)
        self._condition(len(self.posible_eligble_members) >= 1, 
                        "No member of the household with a disability is between the ages of 18-59 (0-59 for blindness)",
                        "A member of the house hold is with a disability is between the ages of 18-59 (0-59 for blindness)")

        #Income
        self.posible_eligble_members = map(self._calc_total_countable_income, self.posible_eligble_members)

        self.posible_eligble_members = filter(lambda m: m["countable_income"] < 248)

        self._condition(len(self.posible_eligble_members) >= 1,
                        "No member of the household with a disability makes less than $248 a month",
                        "A member of the house hold is with a disability makes less than $248 a month")

    def _calc_total_countable_income(self, member):
        earned = member.calc_gross_income("monthly", ["earned"])
        countable_earned = max(0, (earned - 65)/2)

        unearned = member.calc_gross_income("monthly", ["unearned"])
        countable_unearned = max(0, unearned - 20)

        total_countable = countable_earned + countable_unearned

        return {"member": member, "countable_income": total_countable}

    def calc_value(self):
        self.value = 0
        for member in self.posible_eligble_members:
            member_value = max(0, 248 - member["countable_income"])
            self.value += member_value

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