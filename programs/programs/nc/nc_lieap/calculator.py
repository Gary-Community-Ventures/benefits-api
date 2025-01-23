from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class NCLieap(ProgramCalculator):
    expenses = ["rent", "mortgage", "heating"]
    fpl_percent = 1.3
    resource_limit = 2250
    dependencies = ["income_frequency", "income_amount", "zipcode", "household_size"]
    income_limits = {
        # 0-50% FPL 51%-100% FPL
        1: [816, 1632],
        2: [1107, 2214],
        3: [1399, 2797],
        4: [1690, 3380],
        5: [1981, 3963],
        6: [2273, 4546],
        7: [2564, 5129],
        8: [2856, 5711],
        9: [3147, 6294],
        10: [3439, 6877],
        11: [3730, 7460],
        12: [4021, 8043],
        13: [4313, 8626],
        14: [4604, 9208],
        15: [4896, 9791]
    }
    

    def household_eligible(self, e: Eligibility):
        household_size = self.screen.household_size
        gross_income = self.screen.calc_gross_income("monthly", ["all"])
                        
        # has rent or mortgage expense
        has_rent = self.screen.has_expense(["rent"])
        has_mortgage = self.screen.has_expense(["mortgage"])
        e.condition(has_rent or has_mortgage)
        
        # income
        if household_size:
            income_limit = int(self.fpl_percent * self.income_limits[household_size][1])
            
        e.condition(gross_income < income_limit, messages.income(gross_income, income_limit))


    def household_value(self):
        household_size = self.screen.household_size
        gross_income = self.screen.calc_gross_income("monthly", ["all"])

        if household_size:
            if household_size <= 3:
                if gross_income <= self.income_limits[household_size][0]: # 0-50% FPL
                    return 400
                elif gross_income <= self.income_limits[household_size][1]: # 51%-130% FPL
                    return 300
            else:  # Household size >= 4
                if gross_income <= self.income_limits[household_size][0]: # 0-50% FPL
                    return 500
                elif gross_income <= self.income_limits[household_size][1]: # 51%-130% FPL
                    return 400

        return 0