from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class FamilyPlanningServices(ProgramCalculator):
    amount = 404
    min_age = 12
    fpl_percent = 2.65
    dependencies = ["age", "insurance", "income_frequency", "income_amount", "household_size"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Does not have insurance
        has_no_insurance = False
        for member in self.screen.household_members.all():
            has_no_insurance = member.insurance.has_insurance_types(("none",)) or has_no_insurance
        e.condition(has_no_insurance, messages.has_no_insurance())

        # Not Medicaid eligible
        e.condition(not medicaid_eligible(self.data), messages.must_not_have_benefit("Medicaid"))

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: not m.pregnant, None),
                (lambda m: m.age >= FamilyPlanningServices.min_age, None),
                (lambda m: m.is_head() or m.is_spouse(), None),
            ],
        )

        # Income
        fpl = self.program.fpl
        print(fpl.get_limit(self.screen.household_size + e.eligible_member_count))
        income_limit = int(
            FamilyPlanningServices.fpl_percent * fpl.get_limit(self.screen.household_size + e.eligible_member_count)
        )
        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

        return e
