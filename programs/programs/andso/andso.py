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
    grant_standard = 248
    earned_standard_deduction = 65
    unearned_standard_deduction = 20
    asset_limit = 2000
    max_age = 59

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

        #No SSI
        self._condition(not self.screen.has_ssi,
                        "Must not be receiving SSI",
                        "Does not receive SSI")

        # No TANIF
        tanf_eligible = calculate_tanf(self.screen, None)["eligibility"]["eligible"]
        self._condition(not (self.screen.has_tanf or tanf_eligible),
                        "Must not be eligible for TANF",
                        "Is not eligible for TANF")
        #Assets less than limit
        self._condition(self.screen.household_assets < Andso.asset_limit,
                        f"Household assets must not exceed {Andso.asset_limit}",
                        f"Assets are less than the limit of {Andso.asset_limit}")

        # Has disability/blindness
        member_has_blindness = False
        member_has_disability = False
        self.posible_eligble_members = []

        for member in self.screen.household_members.all():
            eligible = False
            if member.disabled:
                member_has_disability = True
                eligible = True
            if member.visually_impaired:
                member_has_blindness = True
                eligible = True
            if eligible:
                self.posible_eligble_members.append(member)
        self._condition(member_has_blindness or member_has_disability,
                        "No one in the household has a disability or blindness",
                        "Someone in the household has a disability or blindness")

        # Right age
        min_age = 0 if member_has_blindness else 18

        for member in self.posible_eligble_members:
            is_in_age_range = self._between(member.age, min_age, Andso.max_age)
            if not is_in_age_range:
                self.posible_eligble_members.remove(member)
        self._condition(len(self.posible_eligble_members) >= 1, 
                        f"No member of the household with a disability is between the ages of 18-{Andso.max_age} (0-{Andso.max_age} for blindness)",
                        f"A member of the house hold is with a disability is between the ages of 18-{Andso.max_age} (0-{Andso.max_age} for blindness)")

        #Income
        def calc_total_countable_income(member):
            earned = member.calc_gross_income("monthly", ["earned"])
            countable_earned = max(0, (earned - Andso.earned_standard_deduction) / 2)

            unearned = member.calc_gross_income("monthly", ["unearned"])
            countable_unearned = max(0, unearned - Andso.unearned_standard_deduction)

            total_countable = countable_earned + countable_unearned

            return {"member": member, "countable_income": total_countable}

        self.posible_eligble_members = map(
            calc_total_countable_income, self.posible_eligble_members)

        self.posible_eligble_members = list(filter(
            lambda m: m["countable_income"] < Andso.grant_standard, self.posible_eligble_members))

        self._condition(len(self.posible_eligble_members) >= 1,
                        f"""No member of the household with a disability has a total
                         countable income less than ${Andso.grant_standard} a month""",
                        f"""A member of the house hold is with a disability has a total
                         countable income less than ${Andso.grant_standard} a month""")


    def calc_value(self):
        self.value = 0
        for member in self.posible_eligble_members:
            member_value = max(0, Andso.grant_standard - member["countable_income"])
            self.value += member_value
        self.value *= 12

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