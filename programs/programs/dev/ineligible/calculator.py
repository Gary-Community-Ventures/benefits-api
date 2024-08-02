from programs.programs.calc import Eligibility, ProgramCalculator


class DevIneligible(ProgramCalculator):
    def eligible(self) -> Eligibility:
        e = Eligibility()

        e.condition(False)

        return e
