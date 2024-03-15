from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from programs.sheets import sheets_get_data
from integrations.util import Cache


class ConnectForHealth(ProgramCalculator):
    percent_of_fpl = 4
    dependencies = ['insurance', 'income_amount', 'income_frequency', 'county', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Medicade eligibility
        is_medicaid_eligible = False
        for benefit in self.data:
            if benefit['name_abbreviated'] == 'medicaid':
                is_medicaid_eligible = benefit['eligible']
                break

        e.condition(not is_medicaid_eligible,
                    messages.must_not_have_benefit('Medicaid'))

        # Someone has no health insurance
        has_no_hi = self.screen.has_insurance_types(('none', 'private'))
        e.condition(has_no_hi,
                    messages.has_no_insurance())
        
        # HH member has no va insurance
        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (
                    lambda m: not m.insurance.has_insurance_types(('va', 'private')),
                    messages.must_not_have_benefit('VA')
                )
            ]
        )

        # Income
        fpl = self.program.fpl.as_dict()
        income_band = int(fpl[self.screen.household_size] / 12 * ConnectForHealth.percent_of_fpl)
        gross_income = int(self.screen.calc_gross_income('yearly', ('all',)) / 12)
        e.condition(gross_income < income_band,
                    messages.income(gross_income, income_band))

        return e

    def value(self, eligible_members: int):    
        limits = cache.fetch()
        return limits[self.screen.county] * 12


class CFHCache(Cache):
    expire_time = 60 * 60 * 24
    default = {}

    def update(self):
        spreadsheet_id = '1SuOhwX5psXsipMS_G5DE_f9jLS2qWxf6temxY445EQg'
        range_name = "'2023 report'!A2:B65"
        sheet_values = sheets_get_data(spreadsheet_id, range_name)

        if not sheet_values:
            raise Exception('Sheet unavailable')
        
        data = {d[0].strip() + ' County': float(d[1].replace(',', '')) for d in sheet_values}

        return data


cache = CFHCache()
