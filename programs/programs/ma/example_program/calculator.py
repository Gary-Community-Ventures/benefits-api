from programs.programs.calc import MemberEligibility, ProgramCalculator


# NOTE: This an example program where each child in the household would get $750
class ExampleCalculator(ProgramCalculator):
    member_amount = 750
    max_age = 18
    dependencies = ["age"]

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age
        e.condition(member.age <= self.max_age)
