from programs.util import Dependencies
from screener.models import Screen
from programs.calc import Eligibility, ProgramCalculator
from .dependencies import PolicyEngineScreenInput
from typing import List
from . import YEAR


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

        if self.value() > 0:
            e.eligible = True

        return e

    def value(self):
        return self.pe_data[self.pe_category][self.pe_sub_category][self.pe_name][self.year]

    def get_data(self):
        return self.pe_data[self.pe_category][self.pe_sub_category]

    def format_month(self) -> str:
        return self.year + '-' + self.month

    def can_calc(self, missing_dependencies: Dependencies):
        for input in self.pe_inputs:
            if missing_dependencies.has(input.dependencies):
                return False

        return True
