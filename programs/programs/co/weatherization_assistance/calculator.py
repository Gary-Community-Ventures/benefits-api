from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class WeatherizationAssistance(ProgramCalculator):
    income_limits = (
        36_983,
        48_362,
        59_742,
        71_122,
        82_501,
        93_881,
        96_014,
        101_120,
    )
    presumptive_eligibility = ("andcs", "ssi", "snap", "leap", "tanf")
    amount = 350
    dependencies = ["household_size", "income_amount", "income_frequency"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # income condition
        income_limit = WeatherizationAssistance.income_limits[self.screen.household_size - 1]
        income = int(self.screen.calc_gross_income("yearly", ["all"]))
        income_eligible = income <= income_limit

        # categorical eligibility
        categorical_eligible = False
        for program in WeatherizationAssistance.presumptive_eligibility:
            if self.screen.has_benefit(program):
                categorical_eligible = True
                break

        e.condition(income_eligible or categorical_eligible, messages.income(income, income_limit))

        return e
