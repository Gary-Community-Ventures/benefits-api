from programs.programs.co.energy_calculator.util import has_renter_expenses
from programs.programs.translation_overrides.base import TranslationOverrideCalculator


class CoEnergyCalculatorRenter(TranslationOverrideCalculator):
    def eligible(self) -> bool:
        """
        Show for renters
        """
        return has_renter_expenses(self.screen)
