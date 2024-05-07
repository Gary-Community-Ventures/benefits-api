import programs.programs.messages as messages
from programs.programs.calc import ProgramCalculator, Eligibility


class CashBack(ProgramCalculator):
    amount = 750
    dependencies = ["age"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        adults = self.screen.num_adults(age_max=18)
        e.condition(adults > 0, messages.older_than(18))

        return e

    def value(self, eligible_members: int):
        adults = self.screen.num_adults(age_max=18)
        value = adults * 750
        return value
