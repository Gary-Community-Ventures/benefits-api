from .base import WarningCalculator
from .ineligible import DontShow


general_calculators = {
    "_show": WarningCalculator,
    "_dont_show": DontShow,
}

specific_caculators = {}

warning_calculators = {**general_calculators, **specific_caculators}
