from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class EmergencyMedicaid(ProgramCalculator):
    amount = 9_540
    dependencies = ["insurance"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Does qualify for Medicaid
        e.condition(medicaid_eligible(self.data), messages.must_have_benefit("Medicaid"))

        e.member_eligibility(
            self.screen.household_members.all(),
            [(lambda m: m.insurance.has_insurance_types(("none",)), messages.has_no_insurance())],
        )

        return e
