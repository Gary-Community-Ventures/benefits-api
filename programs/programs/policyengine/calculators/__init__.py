from programs.programs.federal.pe import (
    federal_member_calculators,
    federal_spm_unit_calculators,
    federal_tax_unit_calculators,
)
from programs.programs.co.pe import co_member_calculators, co_tax_unit_calculators, co_spm_calculators
from programs.programs.nc.pe import nc_member_calculators, nc_spm_calculators
from programs.programs.ma.pe import ma_member_calculators, ma_tax_unit_calculators, ma_spm_calculators
from programs.programs.il.pe import il_member_calculators, il_tax_unit_calculators, il_spm_calculators
from .base import (
    PolicyEngineMembersCalculator,
    PolicyEngineSpmCalulator,
    PolicyEngineTaxUnitCalulator,
    PolicyEngineCalulator,
)


all_member_calculators: dict[str, type[PolicyEngineMembersCalculator]] = {
    **federal_member_calculators,
    **co_member_calculators,
    **nc_member_calculators,
    **ma_member_calculators,
    **il_member_calculators,
}

all_spm_unit_calculators: dict[str, type[PolicyEngineSpmCalulator]] = {
    **federal_spm_unit_calculators,
    **co_spm_calculators,
    **nc_spm_calculators,
    **ma_spm_calculators,
    **il_spm_calculators,
}

all_tax_unit_calculators: dict[str, type[PolicyEngineTaxUnitCalulator]] = {
    **federal_tax_unit_calculators,
    **co_tax_unit_calculators,
    **ma_tax_unit_calculators,
    **il_tax_unit_calculators,
}

all_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **all_member_calculators,
    **all_spm_unit_calculators,
    **all_tax_unit_calculators,
}

all_pe_programs = all_calculators.keys()
