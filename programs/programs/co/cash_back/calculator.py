from screener.models import HouseholdMember
from programs.programs.calc import MemberEligibility, ProgramCalculator


class CashBack(ProgramCalculator):
    member_amount = 750
    min_age = 18
    dependencies = ["age"]

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        e.condition(member.age >= CashBack.min_age)

        return e
