from programs.programs.calc import ProgramCalculator, Eligibility
from programs.co_county_zips import counties_from_zip
import programs.programs.messages as messages


class MyDenver(ProgramCalculator):
    eligible_counties = ['Denver County']
    child_age_min = 5
    child_age_max = 18
    child_relationship = ['child', 'fosterChild', 'stepChild', 'grandChild', 'relatedOther', 'headOfHousehold']
    dependencies = ['age', 'zipcode', 'relationship']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # geography test
        county_eligible = False

        if not self.screen.county:
            counties = counties_from_zip(self.screen.zipcode)
            for county in counties:
                if county in MyDenver.eligible_counties:
                    county_eligible = True
        else:
            if self.screen.county in MyDenver.eligible_counties:
                county_eligible = True

        e.condition(county_eligible, messages.location())

        children = self.screen.num_children(
            age_max=MyDenver.child_age_max,
            age_min=MyDenver.child_age_min,
            child_relationship=MyDenver.child_relationship
        )

        e.condition(children > 0, messages.child(min_age=5))

        return e

    def value(self, eligible_members: int):
        children = self.screen.num_children(
            age_max=MyDenver.child_age_max,
            age_min=MyDenver.child_age_min,
            child_relationship=MyDenver.child_relationship
        )

        return children * 150
