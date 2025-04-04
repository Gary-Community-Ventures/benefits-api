import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.spm import Snap


# TODO: add state specific SPM calculators from PE here
# TODO: add dependency.household.MaStateCode dependency


# NOTE: here is a possible implentation of SNAP for Massachusetts
class MaSnap(Snap):
    pe_inputs = [
        *Snap.pe_inputs,
        dependency.household.MaStateCode,
    ]
