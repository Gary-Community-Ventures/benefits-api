from .tax_unit import TaxUnit
from .base import WarningCalculator
from .dont_show import DontShow


general_calculators: dict[str, type[WarningCalculator]] = {
    "_show": WarningCalculator,
    "_dont_show": DontShow,
    "_tax_unit": TaxUnit,
}

specific_caculators: dict[str, type[WarningCalculator]] = {}

warning_calculators: dict[str, type[WarningCalculator]] = {**general_calculators, **specific_caculators}
