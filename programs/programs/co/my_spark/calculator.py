from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_screen
from screener.models import HouseholdMember


class MySpark(ProgramCalculator):
    member_amount = 1_000
    max_age = 14
    min_age = 11
    county = "Denver County"
    dependencies = ["age", "zipcode"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Qualify for FRL
        is_frl_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == "nslp":
                is_frl_eligible = benefit["eligible"]
                break
        e.condition(is_frl_eligible, messages.must_have_benefit("Free or Reduced Lunch"))

        counties = counties_from_screen(self.screen)

        # Denever County
        e.condition(MySpark.county in counties, messages.location())

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # age
        e.condition(MySpark.min_age <= member.age <= MySpark.max_age)

        return e
