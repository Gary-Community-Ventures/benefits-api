from .member import member_calculators
from .spm import spm_unit_calculators
from .tax import tax_unit_calculators
from .base import PolicyEnigineCalulator

all_calculators: dict[str, type[PolicyEnigineCalulator]] = {
    **member_calculators,
    **spm_unit_calculators,
    **tax_unit_calculators,
}

all_pe_programs = all_calculators.keys()
