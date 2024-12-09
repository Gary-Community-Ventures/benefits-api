from .nc_aca.calculator import ACASubsidiesNC
from .medicaid.emergency_medicaid.calculator import EmergencyMedicaid
from .sun_bucks.calculator import SunBucks

from ..calc import ProgramCalculator

nc_calculators: dict[str, type[ProgramCalculator]] = {
    "nc_aca": ACASubsidiesNC,
    "nc_emergency_medicaid": EmergencyMedicaid,
    "sunbucks": SunBucks,
}
