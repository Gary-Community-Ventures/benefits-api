from .base import ConfigurationData
from screener.models import WhiteLabel


# TODO: Update NC configuration
class NcConfiguarationData(ConfigurationData):
    @classmethod
    def get_white_label(self) -> WhiteLabel:
        return WhiteLabel.objects.get(code="nc")
