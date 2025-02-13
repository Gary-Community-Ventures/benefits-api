from programs.programs.policyengine.calculators.base import PolicyEngineTaxUnitCalulator
import programs.programs.policyengine.calculators.dependencies as dependency


class Eitc(PolicyEngineTaxUnitCalulator):
    pe_name = "eitc"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.TaxUnitDependentDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.tax.Eitc]


class Ctc(PolicyEngineTaxUnitCalulator):
    pe_name = "ctc_value"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.TaxUnitSpouseDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.tax.Ctc]
