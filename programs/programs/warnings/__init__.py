from .base import WarningCalculator
from .dont_show import DontShow


general_calculators: dict[str, WarningCalculator] = {
    "_show": WarningCalculator,
    "_dont_show": DontShow,
}

specific_caculators: dict[str, WarningCalculator] = {}

warning_calculators: dict[str, WarningCalculator] = {**general_calculators, **specific_caculators}
