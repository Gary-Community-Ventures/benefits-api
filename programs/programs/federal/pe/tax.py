from programs.programs.policyengine.calculators.base import PolicyEngineTaxUnitCalulator
from programs.programs.policyengine.calculators.constants import ALL_TAX_UNITS
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
    pe_name = "refundable_ctc"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.TaxUnitSpouseDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.tax.RefundableCtc, dependency.tax.NonRefundableCtc]

    def household_value(self):
        total = 0

        for unit in ALL_TAX_UNITS:
            try:
                total += self.sim.value(self.pe_category, unit, dependency.tax.RefundableCtc.field, self.pe_period)
                total += self.sim.value(self.pe_category, unit, dependency.tax.NonRefundableCtc.field, self.pe_period)
                print(self.sim.value(self.pe_category, unit, dependency.tax.RefundableCtc.field, self.pe_period))
                print(self.sim.value(self.pe_category, unit, dependency.tax.NonRefundableCtc.field, self.pe_period))
            except KeyError:
                pass

        print(total)
        return total
