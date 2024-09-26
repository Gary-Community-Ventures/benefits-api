from programs.programs.calc import MemberEligibility, ProgramCalculator


class Tabor(ProgramCalculator):
    min_age = 18
    member_amount = 800
    dependencies = ["age"]

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age
        e.condition(member.age >= Tabor.min_age)
