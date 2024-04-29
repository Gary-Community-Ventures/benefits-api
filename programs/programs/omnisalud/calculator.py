from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class OmniSalud(ProgramCalculator):
    individual_limit = 1699
    family_4_limit = 3469
    amount = 610
    dependencies = ['income_amount', 'income_frequency', 'household_size', 'age', 'insurance']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Income test
        gross_income = self.screen.calc_gross_income("monthly", ["all"])
        income_band = OmniSalud.family_4_limit if self.screen.household_size >= 4 else OmniSalud.individual_limit
        e.condition(gross_income <= income_band, messages.income(gross_income, income_band))

        # No health insurance
        has_no_hi = self.screen.has_insurance_types(('none',))
        e.condition(has_no_hi, messages.has_no_insurance())

        return e

    def value(self, eligible_members: int):
        return OmniSalud.amount * self.screen.household_size * 12
