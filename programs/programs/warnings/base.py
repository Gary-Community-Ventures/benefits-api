from programs.util import Dependencies
from screener.models import Screen


class WarningCalculator:
    dependencies = tuple()

    def __init__(self, screen: Screen):
        self.screen = screen

    def show(self) -> bool:
        return True

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        """
        Returns whether or not the program can be calculated with the missing dependencies
        """
        return not missing_dependencies.has(*cls.dependencies)
