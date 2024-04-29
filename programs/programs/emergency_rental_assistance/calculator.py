from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages
from integrations.util.cache import Cache
from programs.sheets import sheets_get_data
from programs.co_county_zips import counties_from_zip


class EmergencyRentalAssistanceIncomeLimitsCache(Cache):
    expire_time = 60 * 60 * 24
    default = {}

    def update(self):
        spreadsheet_id = '1QHb-ZT0Y2oWjFMoeP_wy8ClveslINWdehb-CXhB8WSE'
        range_name = "'2022 80% AMI'!A2:I"
        sheet_values = sheets_get_data(spreadsheet_id, range_name)

        if not sheet_values:
            raise Exception('Sheet unavailable')

        data = {d[0].strip() + ' County': [int(v.replace(',', '')) for v in d[1:]] for d in sheet_values}

        return data


class EmergencyRentalAssistance(ProgramCalculator):
    amount = 13_848
    dependencies = ['income_amount', 'income_frequency', 'household_size', 'zipcode']
    income_cache = EmergencyRentalAssistanceIncomeLimitsCache()

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Income test
        counties = counties_from_zip(self.screen.zipcode)
        county_name = self.screen.county if self.screen.county is not None else counties[0]

        income = self.screen.calc_gross_income('yearly', ['all'])
        income_limits = EmergencyRentalAssistance.income_cache.fetch() 
        # NOTE: 80% to income is already applied in the sheet.
        income_limit = income_limits[county_name][self.screen.household_size - 1]
        e.condition(income < income_limit, messages.income(income, income_limit))

        return e

