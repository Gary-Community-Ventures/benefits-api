from programs.programs.federal.pe.tax import Eitc
import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.policyengine.calculators.base import PolicyEngineTaxUnitCalulator


class Maeitc(PolicyEngineTaxUnitCalulator):
    pe_name = "ma_eitc"
    pe_inputs = [*Eitc.dependencies, dependency.household.MaStateCode]
    pe_outputs = [dependency.tax.Maeitc]
