from ._default import DefaultConfigurationData
from .base import ConfigurationData
from .co import CoConfigurationData
from .nc import NcConfigurationData


white_label_config: dict[str, ConfigurationData] = {
    "co": CoConfigurationData,
    "nc": NcConfigurationData,
    "_default": DefaultConfigurationData,
}
