from programs.programs.categories.co.preschool import PreschoolCategoryCap
from ..base import ProgramCategoryCapCalculator

co_category_cap_calculators: dict[str, type[ProgramCategoryCapCalculator]] = {"co_preschool": PreschoolCategoryCap}
