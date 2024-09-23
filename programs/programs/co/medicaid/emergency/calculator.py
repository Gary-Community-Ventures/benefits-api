from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages
from screener.models import HouseholdMember


class EmergencyMedicaid(ProgramCalculator):
    amount = 9_540
    insurance_types = ["none"]
    dependencies = ["insurance"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Does qualify for Medicaid
        e.condition(medicaid_eligible(self.data), messages.must_have_benefit("Medicaid"))

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # insurance
        e.condition(member.insurance.has_insurance_types(EmergencyMedicaid.insurance_types))

        return e
