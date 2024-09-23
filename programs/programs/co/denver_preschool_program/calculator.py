from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_screen
from screener.models import HouseholdMember


class DenverPreschoolProgram(ProgramCalculator):
    member_amount = 788 * 12
    min_age = 3
    max_age = 4
    county = "Denver County"
    dependencies = ["age", "zipcode"]

    def household_eligible(self) -> Eligibility:
        e = Eligibility()

        # Lives in Denver
        counties = counties_from_screen(self.screen)
        e.condition(DenverPreschoolProgram.county in counties, messages.location())

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # age
        e.condition(DenverPreschoolProgram.min_age >= member.age >= DenverPreschoolProgram.max_age)

        return e
