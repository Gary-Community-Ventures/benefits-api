from .nc_weatherization.calculator import NCWeatherization
from .nc_lieap.calculator import NCLieap
from .medicaid.emergency_medicaid.calculator import EmergencyMedicaid
from .sun_bucks.calculator import SunBucks
from .nc_crisis_intervention.calculator import NCCrisisIntervention

from ..calc import ProgramCalculator

nc_calculators: dict[str, type[ProgramCalculator]] = {
    "nc_emergency_medicaid": EmergencyMedicaid,
    "sunbucks": SunBucks,
    "nc_lieap": NCLieap,
    "nccip": NCCrisisIntervention,
    "ncwap": NCWeatherization,
}
