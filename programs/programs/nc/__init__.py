from .nc_aca.calculator import ACASubsidiesNC
from .medicaid.emergency_medicaid.calculator import EmergencyMedicaid

from ..calc import ProgramCalculator

nc_calculators: dict[str, type[ProgramCalculator]] = {
    "nc_aca": ACASubsidiesNC,
    "nc_emergency_medicaid": EmergencyMedicaid,
}
