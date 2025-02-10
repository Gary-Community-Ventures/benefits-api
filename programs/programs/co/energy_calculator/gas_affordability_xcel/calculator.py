from programs.programs.calc import Eligibility, ProgramCalculator
from programs.programs.co.energy_calculator.energy_assistance.calculator import EnergyCalculatorEnergyAssistance
from programs.programs.co.energy_calculator.energy_outreach.calculator import EnergyCalculatorEnergyOutreach
from programs.programs.co.energy_calculator.utility_bill_pay.calculator import EnergyCalculatorUtilityBillPay
from programs.programs.co.energy_calculator.weatherization_assistance.calculator import (
    EnergyCalculatorWeatherizationAssistance,
)


class EnergyCalculatorGasAffordabilityXcel(ProgramCalculator):
    amount = 1
    dependencies = [
        *EnergyCalculatorEnergyAssistance.dependencies,
        *EnergyCalculatorEnergyOutreach.dependencies,
        *EnergyCalculatorWeatherizationAssistance.dependencies,
        *EnergyCalculatorUtilityBillPay.dependencies,
        "energy_calculator",
    ]
    presumptive_eligibility = [
        "energy_calculator_leap",
        "co_energy_calculator_eoc",
        "co_energy_calculator_cowap",
        "co_energy_calculator_ubp",
    ]
    gas_providers = ["co-xcel-energy"]

    def household_eligible(self, e: Eligibility):
        # eligible for another program
        has_another_program = False
        for program in self.presumptive_eligibility:
            eligible = self.data[program].eligible
            if eligible:
                has_another_program = True
        e.condition(has_another_program)

        # has gas provider
        e.condition(self.screen.energy_calculator.has_gas_provider(self.gas_providers))
