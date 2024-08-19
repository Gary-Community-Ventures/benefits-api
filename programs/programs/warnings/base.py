from programs.util import Dependencies
from screener.models import Screen


class WarningCalculator:
    dependencies = tuple()

    def __init__(self, screen: Screen, counties: list[str]):
        self.screen = screen
        self.counties = counties

    def calc(self) -> bool:
        return self.county_eligible() and self.eligible()

    def eligible(self):
        return True

    def county_eligible(self):
        if len(self.counties) == 0:
            return True

        return self.screen.county in self.county

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        """
        Returns whether or not the program can be calculated with the missing dependencies
        """
        return not missing_dependencies.has(*cls.dependencies)
