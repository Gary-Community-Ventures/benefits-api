from programs.programs.nc.pe import spm
import programs.programs.nc.pe.member as member
from programs.programs.policyengine.calculators.base import PolicyEngineCalulator


nc_member_calculators = {"nc_medicaid": member.NcMedicaid, "nc_wic": member.NcWic}
nc_spm_calculators = {"nc_snap": spm.NcSnap}


nc_pe_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **nc_member_calculators,
    **nc_spm_calculators,
}
