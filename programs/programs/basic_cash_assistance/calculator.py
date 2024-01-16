import programs.programs.messages as messages
from programs.programs.calc import Eligibility, ProgramCalculator
from programs.co_county_zips import counties_from_zip


class BasicCashAssistance(ProgramCalculator):
    amount = 1_000
    county = 'Denver County'
    dependencies = ['zipcode', 'age']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Lives in Denver
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        in_denver = BasicCashAssistance.county in counties
        e.condition(in_denver, messages.location())

        # Has a child
        num_children = self.screen.num_children()
        e.condition(num_children >= 1, messages.child())

        return e

    def value(self, eligible_members: int):
        return self.amount
