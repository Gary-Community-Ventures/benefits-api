from programs.models import Program
from programs.programs.policyengine.calculators.constants import MAIN_TAX_UNIT, SECONDARY_TAX_UNIT
from programs.util import Dependencies
from screener.models import Screen
from programs.programs.calc import Eligibility, ProgramCalculator
from .dependencies.base import PolicyEngineScreenInput
from typing import List
from ..engines import Sim


class PolicyEngineCalulator(ProgramCalculator):
    """
    Base class for all Policy Engine programs
    """

    pe_inputs: List[type[PolicyEngineScreenInput]] = []
    pe_outputs: List[type[PolicyEngineScreenInput]] = []

    pe_name = ""
    pe_category = ""
    pe_sub_category = ""

    def __init__(self, screen: Screen, program: Program):
        self.screen = screen
        self.program = program
        self._sim = None

    def set_engine(self, sim: Sim):
        self._sim = sim

    def eligible(self) -> Eligibility:
        e = Eligibility()

        e.value = self.value()
        e.eligible = e.value > 0

        return e

    def value(self):
        return int(self.get_variable())

    @property
    def pe_period(self) -> str:
        if self.program.fpl is None:
            raise Exception(f"the period is not configured for: {self.pe_name}")

        return self.program.fpl.pe_period

    @property
    def sim(self) -> Sim:
        if self._sim is None:
            raise Exception("Engine is not configured")

        return self._sim

    def get_variable(self):
        """
        Return value of the default variable
        """
        return self.sim.value(self.pe_category, self.pe_sub_category, self.pe_name, self.pe_period)

    def get_tax_variable(self, unit: str):
        return self.sim.value(self.pe_category, unit, self.pe_name, self.pe_period)

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        for input in cls.pe_inputs:
            if missing_dependencies.has(*input.dependencies):
                return False

        return True


class PolicyEngineSpmCalulator(PolicyEngineCalulator):
    pe_category = "spm_units"
    pe_sub_category = "spm_unit"


class PolicyEngineTaxUnitCalulator(PolicyEngineCalulator):
    pe_category = "tax_units"
    tax_unit_dependent = True

    def value(self):
        return self.tax_unit_value(MAIN_TAX_UNIT) + self.tax_unit_value(SECONDARY_TAX_UNIT)

    def tax_unit_value(self, unit: str):
        try:
            return int(self.get_tax_variable(unit))
        except KeyError:
            return 0  # if the second tax unit does not exist


class PolicyEngineMembersCalculator(PolicyEngineCalulator):
    tax_unit_dependent = True
    pe_category = "people"

    def value(self):
        total = 0
        for member in self.screen.household_members.all():
            pe_value = self.get_member_variable(member.id)

            total += pe_value

        return total

    def get_member_variable(self, member_id: int):
        return self.sim.value(self.pe_category, str(member_id), self.pe_name, self.pe_period)
