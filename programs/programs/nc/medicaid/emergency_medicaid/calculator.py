from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class EmergencyMedicaid(ProgramCalculator):
    # $6,268/yr | ~$522/mo
    member_amount = 6268
    max_age = 64
    fpl_percent = 1.96
    dependencies = ["age", "insurance", "income_amount", "household_size"]

    def household_eligible(self, e: Eligibility):
        # Does not have insurance
        has_no_insurance = False
        for member in self.screen.household_members.all():
            has_no_insurance = member.insurance.has_insurance_types(("none",)) or has_no_insurance

            # Pregnant and under 18 years old have a different FPL percentage
            if member.age <= 18 and member.pregnant:
                EmergencyMedicaid.fpl_percent = 2.11

        e.condition(has_no_insurance, messages.has_no_insurance())

        # Medicaid eligibility
        e.condition(medicaid_eligible(self.data), messages.must_have_benefit("Medicaid"))

        # Income
        fpl = self.program.fpl
        income_limit = int(
            EmergencyMedicaid.fpl_percent * fpl.get_limit(self.screen.household_size)
        )
        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # pregnant
        e.condition(member.pregnant)

        # age
        e.condition(not member.age >= EmergencyMedicaid.max_age)