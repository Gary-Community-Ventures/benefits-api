from programs.programs.ma.pe import spm
import programs.programs.ma.pe.tax as tax
import programs.programs.ma.pe.member as member
import programs.programs.ma.pe.spm as spm
from programs.programs.policyengine.calculators.base import PolicyEngineCalulator


ma_member_calculators = {
    "ma_wic": member.MaWic,
    "ma_ccdf": member.MaCcdf,
    "ma_mass_health": member.MaMassHealth,
    "ma_mass_health_limited": member.MaMassHealthLimited,
    "ma_mbta": member.MaMbta,
}

ma_tax_unit_calculators = {
    "ma_maeitc": tax.Maeitc,
    "ma_cfc": tax.MaChildFamilyCredit,
}

ma_spm_calculators = {
    "ma_snap": spm.MaSnap,
    "ma_tafdc": spm.MaTafdc,
}

ma_pe_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **ma_member_calculators,
    **ma_tax_unit_calculators,
    **ma_spm_calculators,
}
