from integrations.services.income_limits import ami, smi
from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class WeatherizationAssistance(ProgramCalculator):
    presumptive_eligibility = ("andcs", "ssi", "snap", "leap", "tanf")
    fpl_percent = 2
    ami_percent = "80%"
    smi_percent = 0.6
    amount = 350
    dependencies = ["household_size", "income_amount", "income_frequency", "county"]

    def household_eligible(self, e: Eligibility):
        # income condition
        fpl_limit = self.program.year.as_dict()[self.screen.household_size] * self.fpl_percent
        ami_limit = ami.get_screen_ami(self.screen, self.ami_percent, self.program.year.period)
        smi_limit = smi.get_screen_smi(self.screen, self.program.year.period) * self.smi_percent

        income_limit = max(fpl_limit, ami_limit, smi_limit)

        income = int(self.screen.calc_gross_income("yearly", ["all"]))
        income_eligible = income <= income_limit

        # categorical eligibility
        categorical_eligible = False
        for program in WeatherizationAssistance.presumptive_eligibility:
            if self.screen.has_benefit(program):
                categorical_eligible = True
                break
        e.condition(income_eligible or categorical_eligible, messages.income(income, income_limit))

        # rent or mortgage expense
        e.condition(self._has_expense())

        # utility providers
        e.condition(self._has_utility_provider())

    def _has_expense(self):
        return self.screen.has_expense(["rent", "mortgage"])

    def _has_utility_provider(self):
        return True
