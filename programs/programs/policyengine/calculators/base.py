from programs.util import Dependencies
from screener.models import Screen
from programs.programs.calc import Eligibility, ProgramCalculator
from .dependencies.base import PolicyEngineScreenInput
from typing import List
from .constants import YEAR, PREVIOUS_YEAR


class PolicyEngineCalulator(ProgramCalculator):
    """
    Base class for all Policy Engine programs
    """

    pe_inputs: List[type[PolicyEngineScreenInput]] = []
    pe_outputs: List[type[PolicyEngineScreenInput]] = []

    pe_name = ""
    pe_category = ""
    pe_sub_category = ""
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
        """
        Return Policy Engine dictionary of the program category and subcategory
        """
        return self.pe_data[self.pe_category][self.pe_sub_category]

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        for input in cls.pe_inputs:
            if missing_dependencies.has(*input.dependencies):
                return False

        return True


class PolicyEngineTaxUnitCalulator(PolicyEngineCalulator):
    pe_category = "tax_units"
    pe_sub_category = "tax_unit"
    pe_period = PREVIOUS_YEAR


class PolicyEngineSpmCalulator(PolicyEngineCalulator):
    pe_category = "spm_units"
    pe_sub_category = "spm_unit"


class PolicyEngineMembersCalculator(PolicyEngineCalulator):
    tax_dependent = True
    pe_category = "people"

    def value(self):
        total = 0
        for pkey, pvalue in self.get_data().items():
            # The following programs use income from the tax unit,
            # so we want to skip any members that are not in the tax unit.
            if not self.in_tax_unit(pkey) and self.tax_dependent:
                continue

            pe_value = pvalue[self.pe_name][self.pe_period]

            total += pe_value

        return total

    def in_tax_unit(self, member_id) -> bool:
        return str(member_id) in self.pe_data["tax_units"]["tax_unit"]["members"]

    def get_data(self):
        return self.pe_data[self.pe_category]
