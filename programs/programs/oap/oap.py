from programs.programs.tanf.tanf import calculate_tanf


def calculate_old_age_pension(screen, data):
    old_age_pension = OldAgePension(screen)
    eligibility = old_age_pension.eligibility
    value = old_age_pension.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class OldAgePension():
    grant_standard = 952
    earned_standard_deduction = 65
    unearned_standard_deduction = 20
    asset_limit = 2000
    min_age = 60

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

        # No TANIF
        tanf_eligible = calculate_tanf(self.screen, None)[
            "eligibility"]["eligible"]
        self._condition(not (self.screen.has_tanf or tanf_eligible),
                        "Must not be eligible for TANF")

        # Asset test
        self._condition(self.screen.household_assets < OldAgePension.asset_limit,
                        f"Household assets must not exceed {OldAgePension.asset_limit}")

        # Right age
        self.possible_eligible_members = []

        for member in self.screen.household_members.all():
            if member.age >= OldAgePension.min_age:
                self.possible_eligible_members.append(member)
        self._condition(len(self.possible_eligible_members) >= 1,
                        f"Someone in the household must be {OldAgePension.min_age} or older")

        # Income
        def calc_total_countable_income(member):
            earned = member.calc_gross_income("monthly", ["earned"])
            countable_earned = max(
                0, (earned - OldAgePension.earned_standard_deduction) / 2)

            unearned = member.calc_gross_income("monthly", ["unearned"])
            countable_unearned = max(
                0, unearned - OldAgePension.unearned_standard_deduction)

            total_countable = countable_earned + countable_unearned

            return {"member": member, "countable_income": total_countable}

        self.possible_eligible_members = map(
            calc_total_countable_income, self.possible_eligible_members)

        self.possible_eligible_members = list(filter(
            lambda m: m["countable_income"] < OldAgePension.grant_standard, self.possible_eligible_members))

        self._condition(len(self.possible_eligible_members) >= 1,
                        f"A member of the house hold over the age of {OldAgePension.min_age} must have a countable income less than ${OldAgePension.grant_standard} a month")

    def calc_value(self):
        self.value = 0

        relationship_map = self.screen.relationship_map()
        eligible_members = self.possible_eligible_members
        while len(eligible_members) > 0:
            eligible_member = eligible_members.pop()
            member = eligible_member['member']
            countable_income = eligible_member['countable_income']

            for other_member in eligible_members:
                if other_member['member'].id == relationship_map[member.id]:
                    eligible_members.remove(other_member)
                    break

            # add to total OAP value
            member_value = max(0, OldAgePension.grant_standard - countable_income)
            self.value += member_value

        self.value *= 12

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
