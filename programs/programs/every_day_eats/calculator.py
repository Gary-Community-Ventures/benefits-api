from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class EveryDayEats(ProgramCalculator):
    amount = 600
    min_age = 60
    percent_of_fpl = 1.3
    dependencies = ['age', 'income_amount', 'income_frequency', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Someone older that 60
        num_seniors = self.screen.num_adults(age_max=EveryDayEats.min_age)
        e.condition(num_seniors >= 1, messages.older_than(EveryDayEats.min_age))

        # Income
        fpl = self.program.fpl.as_dict()
        income_limit = EveryDayEats.percent_of_fpl * fpl[self.screen.household_size]
        gross_income = self.screen.calc_gross_income('yearly', ['all'])

        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

        return e

    def value(self, eligible_members: int):
        return EveryDayEats.amount
