from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages
from programs.co_county_zips import counties_from_zip

class Trua(ProgramCalculator):
    income_limit = {
        1: 66_300,
        2: 75_750,
        3: 85_200,
        4: 94_560,
        5: 102_250,
        6: 109_800,
        7: 117_400,
        8: 124_950,
    }

    county = 'Denver County'
    amount = 5568 + 382.83 + 235.68
    dependencies = ['income_amount', 'income_frequency', 'household_size', 'zipcode']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Income test
        gross_income = int(self.screen.calc_gross_income("monthly", ["all"]))
        income_limit = int(Trua.income_limit[self.screen.household_size]/12)
        
        # Location test
        zipcode = self.screen.zipcode
        location = self.screen.county

        if location is not None:
            counties = [location]
        else:
            counties = counties_from_zip(zipcode)

        # Denever County
        e.condition(Trua.county in counties, messages.location())
        
        e.condition(gross_income <= income_limit,
                        messages.income(gross_income, income_limit))
        
        return e