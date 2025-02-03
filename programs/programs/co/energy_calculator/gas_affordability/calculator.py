from programs.programs.calc import Eligibility, ProgramCalculator
from programs.programs.co.energy_calculator.energy_assistance.calculator import EnergyCalculatorEnergyAssistance


class EnergyCalculatorOutreachCrisisIntervention(ProgramCalculator):
    amount = 1
    dependencies = [*EnergyCalculatorEnergyAssistance.dependencies, "energy_calculator"]

    def household_eligible(self, e: Eligibility):
        # eligible for LEAP
        leap_eligible = self.data["energy_calculator_leap"].eligible
        e.condition(leap_eligible)

        # heating is not working
        needs_heating = self.screen.energy_calculator.needs_hvac
        e.condition(needs_heating)
