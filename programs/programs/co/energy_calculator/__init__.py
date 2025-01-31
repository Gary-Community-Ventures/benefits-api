from programs.programs.calc import ProgramCalculator
from programs.programs.co.energy_calculator.affordable_residential_energy.calculator import AffordableResidentialEnergy
from programs.programs.co.energy_calculator.energy_assistance.calculator import EnergyCalculatorEnergyAssistance
from programs.programs.co.energy_calculator.energy_outreach_solar.calculator import EnergyOutreachSolar
from programs.programs.co.energy_calculator.property_credit_rebate.calculator import (
    EnergyCalculatorPropertyCreditRebate,
)
from programs.programs.co.energy_calculator.utility_bill_pay.calculator import EnergyCalculatorUtilityBillPay


co_energy_calculators: dict[str, type[ProgramCalculator]] = {
    "co_energy_calculator_care": AffordableResidentialEnergy,
    "co_energy_calculator_eocs": EnergyOutreachSolar,
    "co_energy_calculator_leap": EnergyCalculatorEnergyAssistance,
    "co_energy_calculator_ubp": EnergyCalculatorUtilityBillPay,
    "co_energy_calculator_cpcr": EnergyCalculatorPropertyCreditRebate,
}
