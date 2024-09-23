from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages
from screener.models import HouseholdMember


class OmniSalud(ProgramCalculator):
    individual_limit = 1699
    family_4_limit = 3469
    insurance = ["none"]
    member_amount = 610 * 12
    dependencies = ["income_amount", "income_frequency", "household_size", "age", "insurance"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Income test
        gross_income = self.screen.calc_gross_income("monthly", ["all"])
        income_band = OmniSalud.family_4_limit if self.screen.household_size >= 4 else OmniSalud.individual_limit
        e.condition(gross_income <= income_band, messages.income(gross_income, income_band))

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # insurance
        e.condition(member.insurance.has_insurance_types(OmniSalud.insurance))

        return e
