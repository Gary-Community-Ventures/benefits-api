from .nc_aca.calculator import ACASubsidiesNC
from ..calc import ProgramCalculator

nc_calculators: dict[str, type[ProgramCalculator]] = {\
    "nc_aca": ACASubsidiesNC,
    
}
