from programs.models import UrgentNeed
from screener.models import Screen
from programs.util import Dependencies


class UrgentNeedFunction:
    """
    Base class for all urgent need conditions
    """

    dependencies = []

    def __init__(self, screen: Screen, urgent_need: UrgentNeed, missing_dependencies: Dependencies, data) -> None:
        self.screen = screen
        self.urgent_need = urgent_need
        print(urgent_need.year)
        self.missing_dependencies = missing_dependencies
        self.data = data

    def calc(self):
        """
        Calculate if the urgent need can be calculated and if the condition is met
        """
        if not self.can_calc():
            return False

        return self.eligible()

    def eligible(self):
        """
        Returns if the condition is met
        """
        return True

    def can_calc(self):
        """
        Returns if the condition can be calculated
        """
        if self.missing_dependencies.has(*self.dependencies):
            return False

        return True
