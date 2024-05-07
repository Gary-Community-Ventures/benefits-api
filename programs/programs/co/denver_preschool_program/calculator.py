from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_zip


class DenverPreschoolProgram(ProgramCalculator):
    amount = 788 * 12
    min_age = 3
    max_age = 4
    county = "Denver County"
    dependencies = ["age", "zipcode"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Has a preschool child
        num_children = self.screen.num_children(
            age_min=DenverPreschoolProgram.min_age,
            age_max=DenverPreschoolProgram.max_age,
        )

        e.condition(
            num_children >= 1,
            messages.child(
                DenverPreschoolProgram.min_age, DenverPreschoolProgram.max_age
            ),
        )

        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        # Lives in Denver
        e.condition(DenverPreschoolProgram.county in counties, messages.location())

        return e
