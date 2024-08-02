from integrations.services.sheets.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_zip
from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class BoulderAmiCache(GoogleSheetsCache):
    sheet_id = "1PRpQ76Xa9Ru0U9MiwgYY5Yfl923lFz4Uu8a4g6A5N6Q"
    range_name = "AMI!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "").replace("$", "")) for a in data[0]]


class NurturingFutures(ProgramCalculator):
    county = "Boulder County"
    head_min_age = 18
    child_max_age = 3
    ami = BoulderAmiCache()
    ami_percent = 0.3
    amount = 3_600

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Lives in Boulder
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)

        e.condition(NurturingFutures.county in counties, messages.location())

        # head is 18+
        e.condition(self.screen.get_head().age >= NurturingFutures.head_min_age)

        # has child 3 or younger
        e.condition(self.screen.num_children(age_max=NurturingFutures.child_max_age))

        # income
        income_limit = NurturingFutures.ami.fetch()[self.screen.household_size - 1] * NurturingFutures.ami_percent
        income = self.screen.calc_gross_income("yearly", ["all"])
        e.condition(income <= income_limit, messages.income(income, income_limit))

        return e
