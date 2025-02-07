from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages


class NCCrisisIntervention(ProgramCalculator):
    expenses = ["rent", "mortgage", "heating", "cooling"]
    fpl_percent = 1.5
    large_household_size = 4
    max_value_fpl_percent = 0.5
    small_household_low_income_value = 400
    small_household_large_income_value = 300
    large_household_low_income_value = 500
    large_household_large_income_value = 400

    dependencies = [
        "household_size",
        "income_amount",
        "income_frequency",
    ]

    def household_eligible(self, e: Eligibility):
        household_size = self.screen.household_size

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(NCCrisisIntervention.expenses)
        e.condition(has_rent_or_mortgage)

        # income
        gross_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = int(self.fpl_percent * self.program.year.as_dict()[household_size])
        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

    def household_value(self):
        household_size = self.screen.household_size
        gross_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = int(self.fpl_percent * self.program.year.as_dict()[household_size])

        if household_size <= self.large_household_size:
            if gross_income <= income_limit * self.max_value_fpl_percent:
                return self.small_household_low_income_value
            elif gross_income <= income_limit:
                return self.small_household_large_income_value
        else:
            if gross_income <= income_limit * self.max_value_fpl_percent:
                return self.large_household_low_income_value
            elif gross_income <= income_limit:
                return self.large_household_large_income_value
