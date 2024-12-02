from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible, snap_eligible, tanf_eligible
import programs.programs.messages as messages


class SunBucks(ProgramCalculator):
    member_amount = 1440
    min_age = 7
    max_age = 16
    fpl_percent = 1.85
    dependencies = ["age", "insurance", "income_amount", "income_frequency", "household_size"]

    def household_eligible(self, e: Eligibility):
        # Income
        fpl = self.program.fpl
        income_limit = int(self.fpl_percent * fpl.get_limit(self.screen.household_size))
        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age eligibility
        child_eligible = False
        if member.age >= SunBucks.min_age and member.age <= SunBucks.max_age:
            child_eligible = True
        
        e.condition(child_eligible)

