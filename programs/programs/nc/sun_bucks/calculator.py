from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages


class SunBucks(ProgramCalculator):
    member_amount = 1440
    min_age = 7
    max_age = 16
    fpl_percent = 1.85
    dependencies = ["age", "insurance", "income_amount", "income_frequency", "household_size"]

    def household_eligible(self, e: Eligibility):
        # Income
        fpl = self.program.year
        income_limit = int(self.fpl_percent * fpl.get_limit(self.screen.household_size))
        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))

        # Must not have the following benefits
        e.condition(not self.screen.has_benefit("snap"), messages.must_not_have_benefit("snap"))
        e.condition(not self.screen.has_benefit("tanf"), messages.must_not_have_benefit("tanf"))
        e.condition(not self.screen.has_benefit("medicaid"), messages.must_not_have_benefit("medicaid"))

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age eligibility
        e.condition(SunBucks.min_age <= member.age <= SunBucks.max_age)
