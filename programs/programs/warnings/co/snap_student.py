from programs.programs.helpers import snap_ineligible_student
from programs.programs.warnings.base import WarningCalculator


class SnapStudentWarning(WarningCalculator):
    dependencies = ['age', ]

    def eligible(self) -> bool:
        for member in self.screen.household_members.all():
            if snap_ineligible_student(self.screen, member):
                return True

        return False
