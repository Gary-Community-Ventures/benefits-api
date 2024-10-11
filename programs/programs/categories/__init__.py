from .base import ProgramCategoryCapCalculator
from .co import co_category_cap_calculators

category_cap_calculators: dict[str, ProgramCategoryCapCalculator] = {
    "no_cap": ProgramCategoryCapCalculator,
    **co_category_cap_calculators,
}