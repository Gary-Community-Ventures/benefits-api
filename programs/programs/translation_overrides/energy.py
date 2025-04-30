from programs.programs.translation_overrides.base import TranslationOverrideCalculator


class CoEnergyCalculatorRenter(TranslationOverrideCalculator):
    def eligible(self) -> bool:
        """
        Show for renters
        """
        print(self.screen.path)
        return self.screen.path == "renter"
