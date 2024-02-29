from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.connect_for_health.tax_credit_value import tax_credit_by_county
import programs.programs.messages as messages


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
        # https://stackoverflow.com/questions/6266727/python-cut-off-the-last-word-of-a-sentence
        return tax_credit_by_county[self.screen.county.rsplit(' ', 1)[0]] * 12
