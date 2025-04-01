from programs.programs.policyengine.calculators.base import PolicyEngineSpmCalulator
import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.spm import Snap


class MaSnap(Snap):
    pe_inputs = [
        *Snap.pe_inputs,
        dependency.household.MaStateCode,
    ]


class MaTafdc(PolicyEngineSpmCalulator):
    field = "ma_tafdc"
    pe_inputs = [
        dependency.household.MaStateCode,
        dependency.spm.MaTanfCountableGrossEarnedIncomeDependency,
        dependency.spm.MaTanfCountableGrossUnearnedIncomeDependency,
        dependency.spm.PreSubsidyChildcareExpenses,
        dependency.household.IsInPublicHousing,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.MaTotalHoursWorked,
        dependency.member.AgeDependency,
    ]

    pe_outputs = [dependency.spm.MaTafdc]
