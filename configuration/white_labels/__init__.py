from ._default import DefaultConfiguarationData
from .base import ConfigurationData
from .co import CoConfiguarationData
from .nc import NcConfiguarationData


white_label_config: dict[str, ConfigurationData] = {
    "co": CoConfiguarationData,
    "nc": NcConfiguarationData,
    "_default": DefaultConfiguarationData,
}
