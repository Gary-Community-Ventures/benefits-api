import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.spm import Snap, Tanf


class NcSnap(Snap):
    pe_inputs = [
        *Snap.pe_inputs,
        dependency.household.NcStateCode,
    ]


class NcTanf(Tanf):
    pe_name = "nc_tanf"
    pe_inputs = [
        *Tanf.pe_inputs,
        dependency.household.NcStateCode,
        dependency.spm.NcTanfCountableEarnedIncomeDependency,
        dependency.spm.NcTanfCountableGrossUnearnedIncomeDependency,
    ]

    pe_outputs = [dependency.spm.NcTanf]
