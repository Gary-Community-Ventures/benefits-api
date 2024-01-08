from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class ReproductiveHealthCare(ProgramCalculator):
    amount = 268
    dependencies = ['insurance']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # No health insurance
        has_no_hi = self.screen.has_insurance_types(('none',))
        e.condition(has_no_hi, messages.has_no_insurance())

        # Medicade eligibility
        is_medicaid_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break

        e.condition(is_medicaid_eligible, messages.must_have_benefit("Medicaid"))

        return e

    def value(self, eligible_members: int):
        return ReproductiveHealthCare.amount
