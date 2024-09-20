import programs.programs.co.pe.tax as tax
import programs.programs.co.pe.member as member
from programs.programs.policyengine.calculators.base import PolicyEngineCalulator


co_member_calculators = {
    "co_medicaid": member.CoMedicaid,
    "andcs": member.AidToTheNeedyAndDisabled,
    "oap": member.OldAgePension,
    "chp": member.Chp,
    "fatc": member.FamilyAffordabilityTaxCredit,
    "co_wic": member.CoWic,
    "ede": member.EveryDayEats,
}

co_tax_unit_calculators = {
    "coeitc": tax.Coeitc,
    "coctc": tax.Coctc,
}

co_pe_calculators: dict[str, type[PolicyEngineCalulator]] = {
    **co_member_calculators,
    **co_tax_unit_calculators,
}
