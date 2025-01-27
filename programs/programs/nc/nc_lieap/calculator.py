from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class NCLieap(ProgramCalculator):
    expenses = ["rent", "mortgage", "heating"]
    fpl_percent = 1.3
    resource_limit = 2250
    dependencies = [
        "income_frequency",
        "income_amount",
        "zipcode",
        "household_size",
        "age",
    ]
    large_household_size = 3
    max_value_fpl_percent = 0.5
    small_household_low_income_value = 400
    small_household_large_income_value = 300
    large_household_low_income_value = 500
    large_household_large_income_value = 400
    has_elder_people = False

    def household_eligible(self, e: Eligibility):
        household_size = self.screen.household_size

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        e.condition(has_rent_or_mortgage)

        # income
        gross_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = int(self.fpl_percent * self.program.fpl.as_dict()[household_size])
        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))

    def household_value(self):
        household_size = self.screen.household_size
        gross_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = int(self.fpl_percent * self.program.fpl.as_dict()[household_size])

        for member in self.screen.household_members.all():
            if member.age > 60:
                self.has_elder_people = True

        if household_size <= self.large_household_size:
            if gross_income <= income_limit * self.max_value_fpl_percent:
                return self.small_household_low_income_value * (4 if self.has_elder_people else 3)
            elif gross_income <= income_limit:
                return self.small_household_large_income_value * (4 if self.has_elder_people else 3)
        else:
            if gross_income <= income_limit * self.max_value_fpl_percent:
                return self.large_household_low_income_value * (4 if self.has_elder_people else 3)
            elif gross_income <= income_limit:
                return self.large_household_large_income_value * (4 if self.has_elder_people else 3)
