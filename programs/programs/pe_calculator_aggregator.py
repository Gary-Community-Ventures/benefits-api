"""
This module aggregates calculator dictionaries from all state modules.
It sits at a higher level to avoid circular imports between state modules
and the policyengine modules.
"""

from programs.programs.policyengine.calculators.base import (
    PolicyEngineMembersCalculator,
    PolicyEngineSpmCalulator,
    PolicyEngineTaxUnitCalulator,
    PolicyEngineCalulator,
)

# Import calculator dictionaries from state modules
from programs.programs.federal.pe import (
    federal_member_calculators,
    federal_spm_unit_calculators,
    federal_tax_unit_calculators,
)
from programs.programs.co.pe import (
    co_member_calculators,
    co_tax_unit_calculators,
    co_spm_calculators,
)
from programs.programs.nc.pe import nc_member_calculators, nc_spm_calculators

# Aggregate calculators by type
all_member_calculators: dict[str, type[PolicyEngineMembersCalculator]] = {
    **federal_member_calculators,
    **co_member_calculators,
    **nc_member_calculators,
}

all_spm_unit_calculators: dict[str, type[PolicyEngineSpmCalulator]] = {
    **federal_spm_unit_calculators,
    **co_spm_calculators,
    **nc_spm_calculators,
}

all_tax_unit_calculators: dict[str, type[PolicyEngineTaxUnitCalulator]] = {
    **federal_tax_unit_calculators,
    **co_tax_unit_calculators,
}

# Combined dictionary with all calculators
all_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **all_member_calculators,
    **all_spm_unit_calculators,
    **all_tax_unit_calculators,
}

# Create a list of all program names
all_pe_programs = all_calculators.keys()
