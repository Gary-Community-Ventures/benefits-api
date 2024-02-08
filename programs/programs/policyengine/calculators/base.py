from programs.util import Dependencies
from screener.models import Screen
from programs.programs.calc import Eligibility, ProgramCalculator
from .dependencies.base import PolicyEngineScreenInput
from ..engines import Sim
from typing import List
from .constants import YEAR


class PolicyEnigineCalulator(ProgramCalculator):
    '''
    Base class for all Policy Engine programs
    '''

    pe_inputs: List[type[PolicyEngineScreenInput]] = []
    pe_outputs: List[type[PolicyEngineScreenInput]] = []

    pe_name = ''
    pe_category = ''
    pe_sub_category = ''
    pe_period = YEAR

    def __init__(self, screen: Screen, sim: Sim):
        self.screen = screen
        self.sim = sim

    def eligible(self) -> Eligibility:
        e = Eligibility()

        e.eligible = self.value() > 0

        return e

    def value(self):
        return int(self.get_variable())

    def get_variable(self):
        '''
        Return value of the default variable
        '''
        return self.sim.value(self.pe_category, self.pe_sub_category, self.pe_name, self.pe_period)

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        for input in cls.pe_inputs:
            if missing_dependencies.has(*input.dependencies):
                return False

        return True
