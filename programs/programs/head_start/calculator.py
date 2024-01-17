from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.programs.head_start.eligible_zipcodes import eligible_zipcode
from programs.co_county_zips import counties_from_zip


class HeadStart(ProgramCalculator):
    amount = 10655
    max_age = 5
    min_age = 3
    dependencies = ['age', 'household_size', 'income_frequency', 'income_amount', 'zipcode']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # has young child
        num_children = self.screen.num_children(age_min=HeadStart.min_age, age_max=HeadStart.max_age)

        e.condition(num_children >= 1, messages.child(HeadStart.min_age, HeadStart.max_age))

        # income
        fpl = self.program.fpl.as_dict()
        income_limit = int(fpl[self.screen.household_size] / 12)
        gross_income = int(self.screen.calc_gross_income('monthly', ['all']))

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

        # location
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        in_eligible_county = False
        for county in counties:
            if county in eligible_zipcode:
                in_eligible_county = True
                break

        e.condition(in_eligible_county, messages.location())

        return e

    def value(self, eligible_members: int):
        return HeadStart.amount
