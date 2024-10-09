from programs.programs.calc import Eligibility
from dataclasses import dataclass


@dataclass
class CategoryCap:
    programs: list[str]
    cap: int = 0


class ProgramCategoryCalculator:
    # caps with a constant max
    static_caps: list[CategoryCap] = []

    # caps where the cap is the highest program value
    max_caps: list[CategoryCap] = []

    # caps where the cap is the average value of the program
    average_caps: list[CategoryCap] = []

    def __init__(self, eligibility: dict[str, Eligibility]):
        self.eligibility = eligibility

    def caps(self):
        return self.static_caps + self.calc_max_caps() + self.calc_average_cap()

    def calc_max_caps(self):
        caps = []

        for max_cap in self.max_caps:
            cap = CategoryCap(max_cap.programs)

            for program in max_cap.programs:
                program_value = self.eligibility[program].value
                if program_value > cap.value:
                    cap.value = program_value

            caps.append(cap)

        return cap

    def calc_average_cap(self):
        caps = []

        for average_cap in self.average_caps:
            total_value = 0

            for program in average_cap.programs:
                total_value += self.eligibility[program].value

            average_value = int(total_value / len(average_cap.programs))
            caps.append(CategoryCap(average_cap.programs, average_value))

        return caps
