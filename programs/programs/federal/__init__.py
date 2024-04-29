from .ssdi.calculator import Ssdi
from .head_start.calculator import HeadStart
from .medicare_savings.calculator import MedicareSavings
from ..calc import ProgramCalculator

federal_calculators: dict[str, type[ProgramCalculator]] = {
    'ssdi': Ssdi,
    'chs': HeadStart,
    'medicare_savings': MedicareSavings,
}
