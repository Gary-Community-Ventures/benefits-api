from .co import co_calculators
from .nc import nc_calculators
from .federal import federal_calculators
from .calc import ProgramCalculator

calculators: dict[str, type[ProgramCalculator]] = {**co_calculators, **nc_calculators, **federal_calculators}
