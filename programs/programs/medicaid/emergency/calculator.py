from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class EmergencyMedicaid(ProgramCalculator):
    amount = 9_540
    dependencies = ['insurance']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Does qualify for Medicaid
        is_medicaid_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break
        e.condition(is_medicaid_eligible, messages.must_have_benefit('Medicaid'))

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (
                    lambda m: m.insurance.has_insurance_types(('none',)),
                    messages.has_no_insurance()
                ),
                (
                    lambda m: m.pregnant,
                    messages.is_pregnant()
                )
            ]
        )

        return e
