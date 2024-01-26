from programs.programs.calc import ProgramCalculator, Eligibility
from programs.co_county_zips import counties_from_zip
import programs.programs.messages as messages


class RtdLive(ProgramCalculator):
    eligible_counties = [
        'Adams County',
        'Arapahoe County',
        'Boulder County',
        'Broomfield County',
        'Denver County',
        'Douglas County',
        'Jefferson County'
    ]
    min_age = 20
    max_age = 64
    percent_of_fpl = 1.85
    amount = 732
    dependencies = ['age', 'income_amount', 'income_frequency', 'zipcode', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # income
        frequency = "yearly"
        income_types = ['all']
        fpl = self.program.fpl.as_dict()
        income_limit = RtdLive.percent_of_fpl * fpl[self.screen.household_size]
        gross_income = self.screen.calc_gross_income(frequency, income_types)
        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

        # age
        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (
                    lambda m: m.age >= RtdLive.min_age and m.age <= RtdLive.max_age,
                    messages.adult(RtdLive.min_age, RtdLive.max_age),
                ),
            ]
        )

        # geography
        county_eligible = False
        if not self.screen.county:
            counties = counties_from_zip(self.screen.zipcode)
        else:
            counties = [self.screen.county]

        for county in counties:
            if county in RtdLive.eligible_counties:
                county_eligible = True

        e.condition(county_eligible, messages.location())

        return e

    def value(self, eligible_members: int):
        return RtdLive.amount * eligible_members
