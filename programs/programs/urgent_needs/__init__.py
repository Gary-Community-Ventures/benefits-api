from .base import UrgentNeedFunction
from .co import co_urgent_need_functions


urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {**co_urgent_need_functions}
