from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class Tabor(ProgramCalculator):
    min_age = 18
    amount = 800
    dependencies = ['age']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.age >= Tabor.min_age, messages.older_than(Tabor.min_age))
            ]
        )

        return e

    def value(self, eligible_members: int):
        return Tabor.amount * eligible_members
