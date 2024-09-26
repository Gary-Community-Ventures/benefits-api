from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages


class EveryDayEats(ProgramCalculator):
    member_amount = 600
    min_age = 60
    percent_of_fpl = 1.3
    dependencies = ["age", "income_amount", "income_frequency", "household_size"]

    def household_eligible(self, e: Eligibility):
        # Income
        fpl = self.program.fpl.as_dict()
        income_limit = EveryDayEats.percent_of_fpl * fpl[self.screen.household_size]
        gross_income = self.screen.calc_gross_income("yearly", ["all"])

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age
        e.condition(member.age >= EveryDayEats.min_age)
