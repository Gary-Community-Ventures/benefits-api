from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class Trua(ProgramCalculator):
    income_limits = {
        1: 66_300,
        2: 75_750,
        3: 85_200,
        4: 94_560,
        5: 102_250,
        6: 109_800,
        7: 117_400,
        8: 124_950,
    }

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Income test
        gross_income = int(self.screen.calc_gross_income("monthly", ["all"]))
        income_band = int(Trua.income_bands[self.screen.household_size]/12)
        
        # Location test
        location = self.screen.county

        e.condition(location == "Denver County",
                        messages.location())
        
        e.condition(gross_income <= income_band,
                        messages.income(gross_income, income_band))
        
        return e
    
    def value(self):
        value = 5568 + 382.83 + 235.68
        return value