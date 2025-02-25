from ._default import DefaultConfigurationData
from .base import ConfigurationData
from .co import CoConfigurationData
from configuration.white_labels.co_energy_calculator import CoEnergyCalculatorConfigurationData
from .nc import NcConfigurationData


white_label_config: dict[str, ConfigurationData] = {
    "_default": DefaultConfigurationData,
    "co": CoConfigurationData,
    "co_energy_calculator": CoEnergyCalculatorConfigurationData,
    "nc": NcConfigurationData,
}
