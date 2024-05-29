from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class MedicaidAdultWithDisability(ProgramCalculator):
    min_age = 16
    max_income_percent = 4.5
    earned_deduction = 65
    earned_percent = 0.5
    amount = 310
    unearned_deduction = 20
    min_age = 16
    insurance_types = ("employer", "private", "none")
    dependencies = ["insurance", "age", "household_size", "income_type", "income_amount", "income_frequency"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Does not qualify for Medicaid
        e.condition(not medicaid_eligible(self.data), messages.must_not_have_benefit("Medicaid"))

        def income_eligible(member):
            fpl = self.program.fpl.as_dict()
            income_limit = fpl[self.screen.household_size] * MedicaidAdultWithDisability.max_income_percent
            earned_deduction = MedicaidAdultWithDisability.earned_deduction
            earned_percent = MedicaidAdultWithDisability.earned_percent
            earned = max(
                0, int((int(member.calc_gross_income("yearly", ["earned"])) - earned_deduction) * earned_percent)
            )
            unearned_deduction = MedicaidAdultWithDisability.unearned_deduction
            unearned = int(member.calc_gross_income("yearly", ["unearned"])) - unearned_deduction
            return earned + unearned <= income_limit

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (
                    lambda m: m.age >= MedicaidAdultWithDisability.min_age,
                    messages.older_than(min_age=MedicaidAdultWithDisability.min_age),
                ),
                (lambda m: m.long_term_disability or m.visually_impaired, messages.has_disability()),
                (lambda m: m.insurance.has_insurance_types(MedicaidAdultWithDisability.insurance_types), None),
                (income_eligible, None),
            ],
        )

        return e

    def value(self, eligible_members: int):
        return MedicaidAdultWithDisability.amount * eligible_members * 12
