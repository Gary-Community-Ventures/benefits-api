from screener.models import WhiteLabel


class WhiteLabelTemplate:
    def __init__(self, white_label: WhiteLabel, source: str) -> None:
        self.white_label = white_label

    def __str__(self) -> str:
        return ""
