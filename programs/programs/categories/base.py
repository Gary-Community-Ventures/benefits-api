from collections.abc import Callable
from programs.programs.calc import Eligibility
from dataclasses import dataclass


@dataclass
class CategoryCap:
    programs: list[str]
    max: int = 0
    member_cap: bool = False


class ProgramCategoryCapCalculator:
    # caps with a constant max
    static_caps: list[CategoryCap] = []

    # caps where the cap is the highest program value
    max_caps: list[CategoryCap] = []

    # caps where the cap is the average value of the program
    average_caps: list[CategoryCap] = []

    def __init__(self, eligibility: dict[str, Eligibility]):
        self.eligibility = eligibility

    def caps(self) -> list[CategoryCap]:
        static_caps = self._handle_caps(self.static_caps, self.calc_static_cap)
        max_caps = self._handle_caps(self.max_caps, self.calc_max_cap)
        average_caps = self._handle_cap(self.average_caps, self.calc_average_cap)

        return static_caps + max_caps + average_caps + self.other_caps()

    def other_caps(self):
        """
        Override this method to add custom caps
        """
        return []

    def calc_static_cap(self, cap: CategoryCap, values: list[int]):
        return cap.max

    def calc_max_cap(self, cap: CategoryCap, values: list[int]):
        return max(*values)

    def calc_average_cap(self, cap: CategoryCap, values: list[int]):
        return sum(values) / len(values)

    def _handle_caps(self, caps: list[CategoryCap], func: Callable[[CategoryCap, list[int]], int]) -> list[CategoryCap]:
        """
        Take a caps and a function and calculate the category caps with that function
        """
        calculated_caps = []

        for cap in caps:
            if cap.member_cap:
                calculated_caps.append(self._handle_member_cap(cap, func))

            calculated_caps.append(self._handle_household_cap(cap, func))

        return calculated_caps

    def _handle_member_cap(self, cap: CategoryCap, func: Callable[[CategoryCap, list[int]], int]) -> CategoryCap:
        """
        Take a cap and a function and calculate the category cap for each member with that function
        """
        member_values: dict[int, list[int]] = {}

        for program in cap.programs:
            eligibility = self.eligibility[program]
            for member_eligibility in eligibility.eligible_members:
                member_id = member_eligibility.member.id

                if member_id not in member_values:
                    member_values[member_id] = []

                member_values[member_id].append(member_eligibility.value)

        cap = CategoryCap(cap.programs)
        for values in member_values.values():
            cap.max += func(values)

        return cap

    def _handle_household_cap(self, cap: CategoryCap, func: Callable[[CategoryCap, list[int]], int]) -> CategoryCap:
        """
        Take a cap and a function and calculate the category cap for the household with that function
        """
        values: list[int] = []

        for program in cap.programs:
            values.append(self.eligibility[program])

        return CategoryCap(cap.programs, func(values))
