from .co import co_calculators
from .federal import federal_calculators
from .dev import dev_calculators
from .calc import ProgramCalculator

calculators: dict[str, type[ProgramCalculator]] = {**co_calculators, **federal_calculators, **dev_calculators}
