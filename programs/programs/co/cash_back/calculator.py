from programs.programs.calc import MemberEligibility, ProgramCalculator


class CashBack(ProgramCalculator):
    member_amount = 750
    min_age = 18
    dependencies = ["age"]

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age
        e.condition(member.age >= CashBack.min_age)
