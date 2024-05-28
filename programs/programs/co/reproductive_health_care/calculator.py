from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class ReproductiveHealthCare(ProgramCalculator):
    amount = 268
    dependencies = ["insurance"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # No health insurance
        has_no_hi = self.screen.has_insurance_types(("none",))
        e.condition(has_no_hi, messages.has_no_insurance())

        # Medicade eligibility
        e.condition(medicaid_eligible(self.data), messages.must_have_benefit("Medicaid"))

        return e
