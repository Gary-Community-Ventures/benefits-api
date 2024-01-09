from programs.util import Dependencies
from screener.models import Screen
from programs.programs.calc import Eligibility, ProgramCalculator
from .dependencies.base import PolicyEngineScreenInput
from typing import List
from .constants import YEAR


class PolicyEnigineCalulator(ProgramCalculator):
    pe_inputs: List[type[PolicyEngineScreenInput]] = []
    pe_outputs: List[type[PolicyEngineScreenInput]] = []

    pe_name = ''
    pe_category = ''
    pe_sub_category = ''
    pe_period = YEAR

    def __init__(self, screen: Screen, pe_data):
        self.screen = screen
        self.pe_data = pe_data

    def eligible(self) -> Eligibility:
        e = Eligibility()

        e.eligible = self.value() > 0

        return e

    def value(self):
        return self.get_data()[self.pe_name][self.pe_period]

    def get_data(self):
        return self.pe_data[self.pe_category][self.pe_sub_category]

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        for input in cls.pe_inputs:
            if missing_dependencies.has(*input.dependencies):
                return False

        return True
