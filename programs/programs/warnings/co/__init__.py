from programs.programs.warnings.base import WarningCalculator
from programs.programs.warnings.co.snap_student import SnapStudentWarning


co_warning_calculators: dict[str, type[WarningCalculator]] = {'co_snap_student': SnapStudentWarning}
