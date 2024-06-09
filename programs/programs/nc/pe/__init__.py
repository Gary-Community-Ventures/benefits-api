import programs.programs.nc.pe.member as member
from programs.programs.policyengine.calculators.base import PolicyEngineCalulator


nc_member_calculators = {
    "nc_medicaid": member.NcMedicaid,
}


nc_pe_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **nc_member_calculators,
}
