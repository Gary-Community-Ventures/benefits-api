from programs.programs.warnings.base import WarningCalculator


class DontShow(WarningCalculator):
    def show(self) -> bool:
        return False
