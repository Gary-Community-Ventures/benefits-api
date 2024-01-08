import programs.programs.messages as messages
from programs.programs.calc import Eligibility, ProgramCalculator


class BasicCashAssistance(ProgramCalculator):
    amount = 1_000
    dependencies = ['county', 'age']

    def eligible(self) -> Eligibility:
        e = Eligibility

        # Lives in Denver
        in_denver = self.screen.county == 'Denver County'
        e.condition(in_denver, messages.location())

        # Has a child
        num_children = self.screen.num_children()
        e.condition(num_children >= 1, messages.child())

        return e

    def value(self):
        return self.amount
