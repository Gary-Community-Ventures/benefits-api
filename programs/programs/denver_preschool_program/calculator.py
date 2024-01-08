from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class DenverPreschoolProgram(ProgramCalculator):
    amount = 788 * 12
    min_age = 3
    max_age = 4
    dependencies = ['age', 'county']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Has a preschool child
        num_children = self.screen.num_children(
            age_min=DenverPreschoolProgram.min_age, age_max=DenverPreschoolProgram.max_age
        )

        e.condition(num_children >= 1,
                    messages.child(DenverPreschoolProgram.min_age, DenverPreschoolProgram.max_age))

        # Lives in Denver
        e.condition(self.screen.county == "Denver County",
                    messages.location())

        return e

    def value(self):
        self.value = DenverPreschoolProgram.amount
