import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.spm import Tanf

class CoTanf(Tanf):
    pe_name = "co_tanf"
    pe_inputs = [
        *Tanf.pe_inputs,
        dependency.household.CoStateCode,
        dependency.member.PregnancyDependency,
        dependency.spm.TanfCountableGrossIncomeDependency,
        dependency.spm.TanfCountableGrossUnearnedIncomeDependency,
    ]
