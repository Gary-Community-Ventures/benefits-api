from ..calc import ProgramCalculator
from .medicaid.emergency.calculator import EmergencyMedicaid
from .medicaid.adult_with_disability.calculator import MedicaidAdultWithDisability

il_calculators: dict[str, type[ProgramCalculator]] = {
    "il_emergency_medicaid": EmergencyMedicaid,
    "il_awd_medicaid": MedicaidAdultWithDisability,
}
