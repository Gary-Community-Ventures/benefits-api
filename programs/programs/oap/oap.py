from programs.programs.tanf.tanf import calculate_tanf


def calculate_oap(screen, data):
    old_age_pension = OldAge(screen)
    eligibility = old_age_pension.eligibility
    value = old_age_pension.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class OldAge():
    grant_standard = 879
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

        #asset test
        self._condition(self.screen.household_assets < OldAge.asset_limit,
                        f"Household assets must not exceed {OldAge.asset_limit}")

        # Right age
        self.possible_eligible_members = []

        for member in self.screen.household_members.all():
            if member.age >= OldAge.min_age:
                self.possible_eligible_members.append(member)
        self._condition(len(self.possible_eligible_members) >= 1,
                        f"Someone in the household must be {OldAge.min_age} or older")

        # Income
        def calc_total_countable_income(member):
            earned = member.calc_gross_income("monthly", ["earned"])
            countable_earned = max(
                0, (earned - OldAge.earned_standard_deduction) / 2)

            unearned = member.calc_gross_income("monthly", ["unearned"])
            countable_unearned = max(
                0, unearned - OldAge.unearned_standard_deduction)

            total_countable = countable_earned + countable_unearned

            return {"member": member, "countable_income": total_countable}

        self.possible_eligible_members = map(
            calc_total_countable_income, self.possible_eligible_members)

        self.possible_eligible_members = list(filter(
            lambda m: m["countable_income"] < OldAge.grant_standard, self.possible_eligible_members))

        self._condition(len(self.possible_eligible_members) >= 1,
                        f"A member of the house hold over the age of {OldAge.min_age} must make less than ${OldAge.grant_standard} a month")

    def calc_value(self):
        self.value = 0

        # remove any possible couples
        possible_couples = set()
        for possible_eligible_member in self.possible_eligible_members:
            member = possible_eligible_member['member']
            countable_income = possible_eligible_member['countable_income']

            if member.id not in possible_couples:
                # Check if there is a couple, and only count SSI for one couple
                # This means that the Old Age Pension might be inacurate for couples

                if member.relationship == 'headOfHousehold':
                    for household_member in self.possible_eligible_members:
                        if household_member['member'].relationship in ('spouse', 'domesticPartner'):
                            # head of house married to this person
                            possible_couples.add(household_member['member'].id)
                            break
                elif member.relationship in ('spouse', 'domesticPartner'):
                    # married to head of house
                    possible_couples.add(
                        self.screen.household_members.filter(relationship='headOfHousehold')[0].id)
                elif member.relationship in ('parent', 'fosterParent', 'stepParent', 'grandParent'):
                    # might be married to someone with same relationship to head of house
                    for person in self.possible_eligible_members:
                        person = person['member']
                        if person.relationship == member.relationship and person.id != member.id:
                            # first other person with same relationship is excluded
                            # only works for first couple
                            possible_couples.add(person.id)
                            break

                # add to total AND-SO value
                member_value = max(0, OldAge.grant_standard - countable_income)
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