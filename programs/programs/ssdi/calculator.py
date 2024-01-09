from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
import math


class Ssdi(ProgramCalculator):
    income_limit = 1_550
    income_limit_blind = 2_590
    amount = 1_537
    dependencies = ['income_amount', 'income_frequency', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        lowest_income = math.inf

        def income_condition(member):
            nonlocal lowest_income

            income_limit = Ssdi.income_limit_blind if member.visually_impaired else Ssdi.income_limit
            member_income = member.calc_gross_income('monthly', ('all',))

            if member_income < lowest_income:
                lowest_income = member_income

            return member_income < income_limit

        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.has_disability(), messages.has_disability()),
                (income_condition, None)
            ]
        )

        e.passed(messages.income(lowest_income, Ssdi.income_limit))

        return e

    def value(self, eligible_members: int):
        return Ssdi.amount * eligible_members * 12
