from programs.programs.ma.pe import spm
import programs.programs.ma.pe.tax as tax
import programs.programs.ma.pe.member as member
import programs.programs.ma.pe.spm as spm
from programs.programs.policyengine.calculators.base import PolicyEngineCalulator


ma_member_calculators = {
    "ma_medicaid": member.MaMedicaid,
    "ma_wic": member.MaWic,
}

ma_tax_unit_calculators = {"ma_maeitc": tax.Maeitc}

ma_spm_calculators = {
    "ma_snap": spm.MaSnap,
}

ma_pe_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **ma_member_calculators,
    **ma_tax_unit_calculators,
    **ma_spm_calculators,
}
