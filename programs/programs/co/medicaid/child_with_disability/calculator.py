from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class MedicaidChildWithDisability(ProgramCalculator):
    max_age = 18
    max_income_percent = 3
    earned_deduction = 90
    income_percent = 1 - 0.33
    insurance_types = ("employer", "private", "none")
    amount = 200
    dependencies = ["insurance", "age", "household_size", "income_type", "income_amount", "income_frequency"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Does not qualify for Medicaid
        is_medicaid_eligible = self.screen.has_insurance_types(["medicaid"])
        for benefit in self.data:
            if benefit["name_abbreviated"] == "medicaid":
                is_medicaid_eligible = benefit["eligible"]
                break
        e.condition(not is_medicaid_eligible, messages.must_not_have_benefit("Medicaid"))

        fpl = self.program.fpl.as_dict()
        income_limit = fpl[self.screen.household_size] * MedicaidChildWithDisability.max_income_percent
        earned = max(
            0, int(self.screen.calc_gross_income("yearly", ["earned"]) - MedicaidChildWithDisability.earned_deduction)
        )
        unearned = self.screen.calc_gross_income("yearly", ["unearned"])
        income = (earned + unearned) * MedicaidChildWithDisability.income_percent
        e.condition(income <= income_limit, messages.income(income, income_limit))

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.age <= MedicaidChildWithDisability.max_age, messages.child()),
                (lambda m: m.long_term_disability or m.visually_impaired, messages.has_disability()),
                (lambda m: m.insurance.has_insurance_types(MedicaidChildWithDisability.insurance_types), None),
                (lambda m: not (m.calc_gross_income("yearly", ["earned"]) >= 0 and m.age >= 16), None),
            ],
        )

        return e

    def value(self, eligible_members: int):
        return MedicaidChildWithDisability.amount * eligible_members * 12
