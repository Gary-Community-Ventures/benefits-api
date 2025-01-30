from programs.programs.calc import ProgramCalculator
from programs.programs.co.energy_calculator.affordable_residential_energy.calculator import AffordableResidentialEnergy


co_energy_calculators: dict[str, type[ProgramCalculator]] = {"co_energy_calculator_care": AffordableResidentialEnergy}
