from programs.programs.calc import MemberEligibility, ProgramCalculator
from screener.models import HouseholdMember


class UniversalPreschool(ProgramCalculator):
    qualifying_age = 3
    age = 4
    percent_of_fpl = 2.7
    amount_by_hours = {"10_hours": 4_837, "15_hours": 6_044, "30_hours": 10_655}
    dependencies = ["age", "income_amount", "income_frequency", "relationship", "household_size"]

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # qualifying condition
        qualifying_condition = self._has_qualifying_condition()

        # age
        min_age = UniversalPreschool.qualifying_age if qualifying_condition else UniversalPreschool.age
        e.condition(min_age <= member.age <= UniversalPreschool.age)

        return e

    def member_value(self, member: HouseholdMember):
        qualifying_condition = self._has_qualifying_condition()

        if not qualifying_condition:
            return UniversalPreschool.amount_by_hours["15_hours"]

        if member.age == UniversalPreschool.age:
            return UniversalPreschool.amount_by_hours["30_hours"]

        return UniversalPreschool.amount_by_hours["10_hours"]

    def _has_qualifying_condition(self, member: HouseholdMember):
        fpl = self.program.fpl.as_dict()
        income_limit = int(UniversalPreschool.percent_of_fpl * fpl[self.screen.household_size])
        income_condition = self.screen.calc_gross_income("yearly", ["all"]) < income_limit

        return income_condition or member.relationship == "fosterChild"
