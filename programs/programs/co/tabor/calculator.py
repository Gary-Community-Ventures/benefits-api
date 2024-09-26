from programs.programs.calc import ProgramCalculator
from screener.models import HouseholdMember


class Tabor(ProgramCalculator):
    min_age = 18
    member_amount = 800
    dependencies = ["age"]

    def member_eligible(self, member: HouseholdMember, e: Eligibility):
        # age
        e.condition(member.age >= Tabor.min_age)
