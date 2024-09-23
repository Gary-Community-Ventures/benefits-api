from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages
from screener.models import HouseholdMember


class ReproductiveHealthCare(ProgramCalculator):
    amount = 268
    dependencies = ["insurance"]

    def household_eligible(self) -> Eligibility:
        e = Eligibility()

        # Medicade eligibility
        e.condition(medicaid_eligible(self.data), messages.must_have_benefit("Medicaid"))

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # No health insurance
        has_no_hi = member.insurance.has_insurance_types(("none",))
        e.condition(has_no_hi)

        return e
