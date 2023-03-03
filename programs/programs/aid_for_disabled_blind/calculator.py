from programs.programs.tanf.calculator import calculate_tanf
import programs.programs.messages as messages


def calculate_aid_for_disabled_blind(screen, data):
    andcs = AidForDisabledBlind(screen)
    eligibility = andcs.eligibility
    value = andcs.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class AidForDisabledBlind():
    grant_standard = 841
    earned_standard_deduction = 65
    unearned_standard_deduction = 20
    asset_limit = 2000
    min_age = 0
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

        # Has SSI
        self._condition(self.screen.has_ssi,
                        messages.must_have_benefit('SSI'))

        # No TANIF
        tanf_eligible = calculate_tanf(self.screen, None)[
            "eligibility"]["eligible"]
        self._condition(not (self.screen.has_tanf or tanf_eligible),
                        messages.must_not_have_benefit('TANF'))

        # Asset test
        self._condition(self.screen.household_assets < AidForDisabledBlind.asset_limit,
                        messages.assets(AidForDisabledBlind.asset_limit))

        # Has disability/blindness
        self.possible_eligible_members = []

        for member in self.screen.household_members.all():
            if member.disabled is True or member.visually_impaired is True:
                self.possible_eligible_members.append(member)

        self._condition(len(self.possible_eligible_members) >= 1,
                        messages.has_disability())

        # Right age
        for member in self.possible_eligible_members:
            is_in_age_range = self._between(member.age, AidForDisabledBlind.min_age, AidForDisabledBlind.max_age)
            if not is_in_age_range:
                self.possible_eligible_members.remove(member)
        self._condition(len(self.possible_eligible_members) >= 1,
                        messages.adult(min_age=AidForDisabledBlind.min_age,
                                       max_age=AidForDisabledBlind.max_age))

        # Income
        def calc_total_countable_income(member):
            earned = member.calc_gross_income("monthly", ["earned"])
            countable_earned = max(0, (earned - AidForDisabledBlind.earned_standard_deduction) / 2)

            unearned = member.calc_gross_income("monthly", ["unearned"])
            countable_unearned = max(0, unearned - AidForDisabledBlind.unearned_standard_deduction)

            total_countable = countable_earned + countable_unearned

            return {"member": member, "countable_income": total_countable}

        self.possible_eligible_members = map(
            calc_total_countable_income, self.possible_eligible_members)

        self.possible_eligible_members = list(filter(
            lambda m: m["countable_income"] < AidForDisabledBlind.grant_standard, self.possible_eligible_members))

        all_members_countable_income = map(calc_total_countable_income, list(self.screen.household_members.all()))
        lowest_income = min(all_members_countable_income,
                            key=lambda m: m["countable_income"])["countable_income"]
        self._condition(len(self.possible_eligible_members) >= 1,
                        messages.income(lowest_income, AidForDisabledBlind.grant_standard))

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

            # add to total AND-CS value
            member_value = max(0, AidForDisabledBlind.grant_standard - countable_income)
            self.value += member_value

        self.value = int(self.value * 12)

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

    def _between(self, value, min_val, max_val):
        return min_val <= value <= max_val
