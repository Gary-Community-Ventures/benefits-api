from programs.programs.ma.pe import spm
import programs.programs.ma.pe.tax as tax
import programs.programs.ma.pe.member as member
import programs.programs.ma.pe.spm as spm
from programs.programs.policyengine.calculators.base import PolicyEngineCalulator


# TODO: update /programs/programs/policyengine/calculators/__init__.py
ma_member_calculators = {  # TODO: add state specific member benefits from PE
    "ma_medicaid": member.MaMedicaid,
}

ma_tax_unit_calculators = {}  # TODO: add state specific tax benefits from PE

ma_spm_calculators = {  # TODO: add state specific SPM benefits from PE
    "ma_snap": spm.MaSnap,
}

ma_pe_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **ma_member_calculators,
    **ma_tax_unit_calculators,
    **ma_spm_calculators,
}
