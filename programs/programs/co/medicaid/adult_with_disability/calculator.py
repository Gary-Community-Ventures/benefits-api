from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from programs.programs.co.medicaid.child_with_disability.calculator import MedicaidChildWithDisability
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages
from screener.models import HouseholdMember


class MedicaidAdultWithDisability(ProgramCalculator):
    min_age = 16
    max_income_percent = 4.5
    earned_deduction = 65
    earned_percent = 0.5
    unearned_deduction = 20
    min_age = 16
    insurance_types = ("employer", "private", "none")
    dependencies = ["insurance", "age", "household_size", "income_type", "income_amount", "income_frequency"]
    member_amount = 310

    def household_eligible(self) -> Eligibility:
        e = Eligibility()

        # Does not qualify for Medicaid
        e.condition(not medicaid_eligible(self.data), messages.must_not_have_benefit("Medicaid"))

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # age
        e.condition(member.age >= MedicaidChildWithDisability.min_age)

        # disability
        e.condition(member.long_term_disability or member.visually_impaired)

        # insurance
        e.condition(member.insurance.has_insurance_types(MedicaidAdultWithDisability.insurance_types))

        # income
        fpl = self.program.fpl.as_dict()
        income_limit = fpl[self.screen.household_size] * MedicaidAdultWithDisability.max_income_percent
        earned_deduction = MedicaidAdultWithDisability.earned_deduction
        earned_percent = MedicaidAdultWithDisability.earned_percent
        earned = max(0, int((int(member.calc_gross_income("yearly", ["earned"])) - earned_deduction) * earned_percent))
        unearned_deduction = MedicaidAdultWithDisability.unearned_deduction
        unearned = int(member.calc_gross_income("yearly", ["unearned"])) - unearned_deduction
        e.condition(earned + unearned <= income_limit)

        return e
