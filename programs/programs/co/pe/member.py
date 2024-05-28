from programs.programs.policyengine.calculators.base import PolicyEngineMembersCalculator
from programs.programs.federal.pe.member import Medicaid
import programs.programs.policyengine.calculators.dependencies as dependency


class CoMedicaid(Medicaid):
    child_medicaid_average = 200 * 12
    adult_medicaid_average = 310 * 12
    aged_medicaid_average = 170 * 12


class AidToTheNeedyAndDisabled(PolicyEngineMembersCalculator):
    pe_name = 'co_state_supplement'
    pe_inputs = [
        dependency.member.SsiCountableResourcesDependency,
        dependency.member.SsiReportedDependency,
        dependency.member.IsBlindDependency,
        dependency.member.IsDisabledDependency,
        dependency.member.SsiEarnedIncomeDependency,
        dependency.member.SsiUnearnedIncomeDependency,
        dependency.member.AgeDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.TaxUnitHeadDependency,
        dependency.member.TaxUnitDependentDependency,
    ]
    pe_outputs = [dependency.member.Andcs]


class OldAgePension(PolicyEngineMembersCalculator):
    pe_name = 'co_oap'
    pe_inputs = [
        dependency.member.SsiCountableResourcesDependency,
        dependency.member.SsiEarnedIncomeDependency,
        dependency.member.SsiUnearnedIncomeDependency,
        dependency.member.AgeDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.TaxUnitHeadDependency,
        dependency.member.TaxUnitDependentDependency,
    ]
    pe_outputs = [dependency.member.Oap]


class Chp(PolicyEngineMembersCalculator):
    pe_name = 'co_chp'
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.PregnancyDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.member.ChpEligible]

    amount = 200 * 12

    def value(self):
        total = 0

        for _, pvalue in self.get_data().items():
            if pvalue['co_chp_eligible'][self.pe_period] > 0 and self.screen.has_insurance_types(('none',)):
                total += self.amount

        return total
