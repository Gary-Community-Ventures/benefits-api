from programs.models import Program
from programs.programs.policyengine.calculators.constants import MAIN_TAX_UNIT, SECONDARY_TAX_UNIT
from programs.util import Dependencies, DependencyError
from screener.models import HouseholdMember, Screen
from programs.programs.calc import Eligibility, MemberEligibility, ProgramCalculator
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

    def __init__(self, screen: Screen, program: "Program", missing_dependencies: Dependencies):
        self.screen = screen
        self.program = program
        self.missing_dependencies = missing_dependencies
        self._sim = None

    def set_engine(self, sim: Sim):
        self._sim = sim

    def eligible(self) -> Eligibility:
        e = super().eligible()

        e.eligible = e.value > 0

        return e

    def household_eligible(self, e: Eligibility):
        household_value = self.household_value()

        e.household_value = household_value

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        member_value = self.member_value(member)

        e.value = member_value
        e.condition(member_value > 0)

    def household_value(self):
        return int(self.get_variable())

    def calc(self) -> Eligibility:
        if not self.can_calc():
            raise DependencyError()

        eligibility = self.eligible()

        return eligibility

    @property
    def pe_period(self) -> str:
        if self.program.fpl is None:
            raise Exception(f"the period is not configured for: {self.pe_name}")

        return self.program.fpl.period

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

    def can_calc(self):
        for input in self.pe_inputs:
            if self.missing_dependencies.has(*input.dependencies):
                return False

        return super().can_calc()


class PolicyEngineSpmCalulator(PolicyEngineCalulator):
    pe_category = "spm_units"
    pe_sub_category = "spm_unit"


class PolicyEngineTaxUnitCalulator(PolicyEngineCalulator):
    pe_category = "tax_units"

    def household_value(self):
        return self.tax_unit_value(MAIN_TAX_UNIT) + self.tax_unit_value(SECONDARY_TAX_UNIT)

    def tax_unit_value(self, unit: str):
        try:
            return int(self.get_tax_variable(unit))
        except KeyError:
            return 0  # if the second tax unit does not exist


class PolicyEngineMembersCalculator(PolicyEngineCalulator):
    pe_category = "people"

    def household_value(self):
        return 0

    def member_value(self, member: HouseholdMember):
        return self.get_member_variable(member.id)

    def get_member_variable(self, member_id: int):
        return self.sim.value(self.pe_category, str(member_id), self.pe_name, self.pe_period)
