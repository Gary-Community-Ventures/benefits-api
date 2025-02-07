from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from screener.models import Insurance


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

    def household_eligible(self, e: Eligibility):
        # no other children
        e.condition(self.screen.num_children(child_relationship=NurseFamilyPartnership.child_relationships) == 0)

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # pregnant
        e.condition(member.pregnant)

        # income
        income_limit = self.program.year.as_dict()[2] * NurseFamilyPartnership.fpl_percent
        income = member.calc_gross_income("yearly", ["all"])
        is_income_eligible = income <= income_limit

        insurance: Insurance = member.insurance
        has_medicaid = insurance.medicaid or insurance.emergency_medicaid
        has_wic = self.screen.has_benefit("wic")

        e.condition(is_income_eligible or has_medicaid or has_wic)
