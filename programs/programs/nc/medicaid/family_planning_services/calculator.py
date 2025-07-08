from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class NCFamilyPlanningServices(ProgramCalculator):
    member_amount = 404
    min_age = 12
    fpl_percent = 1.95
    medicaid_fpl_limit = 1.38
    dependencies = ["age", "insurance", "income_frequency", "income_amount", "household_size"]
    insurance_types = ("none", "employer", "private", "va", "medicare")

    def household_eligible(self, e: Eligibility):
        # Does not have insurance
        has_no_insurance = False

        for member in self.screen.household_members.all():
            has_no_insurance = (
                member.insurance.has_insurance_types(NCFamilyPlanningServices.insurance_types) or has_no_insurance
            )

        e.condition(has_no_insurance, messages.has_no_insurance())

        # Income
        fpl = self.program.year

        income_limit = int(NCFamilyPlanningServices.fpl_percent * fpl.get_limit(len(e.eligible_members)))
        gross_income = int(self.screen.calc_gross_income("yearly", ["all"], exclude=["cashAssistance"]))

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

        income_limit_for_medicaid = int(
            NCFamilyPlanningServices.medicaid_fpl_limit * fpl.get_limit(len(e.eligible_members))
        )
        if gross_income < income_limit_for_medicaid:
            e.condition(not medicaid_eligible(self.data), messages.must_not_have_benefit("Medicaid"))

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # not pregnant
        e.condition(not member.pregnant)

        # age
        e.condition(member.age >= NCFamilyPlanningServices.min_age)

        # head or spouse
        e.condition(member.is_head() or member.is_spouse())
