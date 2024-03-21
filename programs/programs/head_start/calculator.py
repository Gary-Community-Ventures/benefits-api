from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.programs.head_start.eligible_zipcodes import eligible_zipcode
from programs.county_zips import ZipcodeLookup


class HeadStart(ProgramCalculator):
    amount = 10655
    max_age = 5
    min_age = 3
    adams_percent_of_fpl = 1.3  # Adams County uses 130% FPL instead of 100% FPL
    adams_county = 'Adams County'
    dependencies = ['age', 'household_size',
                    'income_frequency', 'income_amount', 'zipcode']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        zipcode_lookup = ZipcodeLookup()

        # has young child
        num_children = self.screen.num_children(
            age_min=HeadStart.min_age, age_max=HeadStart.max_age)

        e.condition(num_children >= 1, messages.child(
            HeadStart.min_age, HeadStart.max_age))

        # location
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = zipcode_lookup.counties_from_zip(self.screen.zipcode)

        in_eligible_county = False
        for county in counties:
            if county in eligible_zipcode:
                in_eligible_county = True
                break

        e.condition(in_eligible_county, messages.location())

        in_adams = HeadStart.adams_county in counties

        # income
        fpl = self.program.fpl.as_dict()
        income_limit = int(fpl[self.screen.household_size] / 12)
        income_limit_adams_county = int(
            fpl[self.screen.household_size] / 12 * HeadStart.adams_percent_of_fpl)
        gross_income = int(self.screen.calc_gross_income('monthly', ['all']))

        if in_adams:
            e.condition(gross_income < income_limit_adams_county,
                        messages.income(gross_income, income_limit_adams_county))
        else:
            e.condition(gross_income < income_limit,
                        messages.income(gross_income, income_limit))

        return e
