from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
from screener.models import HouseholdMember, Insurance


class NurseFamilyPartnership(ProgramCalculator):
    fpl_percent = 2
    child_relationships = ["child", "grandChild"]
    amount = 15_000
    dependencies = [
        "relationship",
        "income_frequency",
        "income_amount",
        "age",
        "pregnant",
    ]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # no other children
        e.condition(self.screen.num_children(child_relationship=NurseFamilyPartnership.child_relationships) == 0)

        def income_eligible(member: HouseholdMember):
            income_limit = self.program.fpl.as_dict()[2] * NurseFamilyPartnership.fpl_percent

            income = member.calc_gross_income("yearly", ["all"])

            is_income_eligible = income <= income_limit

            insurance: Insurance = member.insurance
            has_medicaid = insurance.medicaid or insurance.emergency_medicaid

            has_wic = self.screen.has_benefit("wic")

            return is_income_eligible or has_medicaid or has_wic

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.pregnant, messages.is_pregnant()),
                (income_eligible, None),
            ],
        )

        return e
