from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from screener.models import HouseholdMember


class NurseFamilyPartnership(ProgramCalculator):
    fpl_percent = 2
    amount = 15_000

    def eligible(self) -> Eligibility:
        e = Eligibility()

        def income_eligible(member: HouseholdMember):
            income_limit = self.program.fpl.as_dict()[2] * NurseFamilyPartnership.fpl_percent

            income = member.calc_gross_income('yearly', ['all'])

            return income <= income_limit


        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.pregnant, messages.is_pregnant()),
                (income_eligible, None),
            ]
        )

        return e

