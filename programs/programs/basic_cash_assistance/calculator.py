import programs.programs.messages as messages
from programs.programs.calc import Eligibility, ProgramCalculator
from programs.county_zips import ZipcodeLookup


class BasicCashAssistance(ProgramCalculator):
    amount = 1_000
    county = 'Denver County'
    dependencies = ['zipcode', 'age']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        zipcode_lookup = ZipcodeLookup()

        # Lives in Denver
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = zipcode_lookup.counties_from_zip(self.screen.zipcode)

        in_denver = BasicCashAssistance.county in counties
        e.condition(in_denver, messages.location())

        # Has a child
        num_children = self.screen.num_children()
        e.condition(num_children >= 1, messages.child())

        return e
