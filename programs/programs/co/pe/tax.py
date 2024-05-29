from programs.programs.policyengine.calculators.base import PolicyEngineTaxUnitCalulator
from programs.programs.federal.pe.tax import Eitc
import programs.programs.policyengine.calculators.dependencies as dependency


class Coeitc(PolicyEngineTaxUnitCalulator):
    pe_name = "co_eitc"
    pe_inputs = [
        *Eitc.pe_inputs,
        dependency.household.CoStateCode,
    ]
    pe_outputs = [dependency.tax.Coeitc]


class Coctc(PolicyEngineTaxUnitCalulator):
    pe_name = "ctc"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.household.CoStateCode,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.tax.Ctc]

    income_bands = {
        "single": [{"max": 25000, "percent": 0.6}, {"max": 50000, "percent": 0.3}, {"max": 75000, "percent": 0.1}],
        "maried": [{"max": 35000, "percent": 0.6}, {"max": 60000, "percent": 0.3}, {"max": 85000, "percent": 0.1}],
    }

    def value(self):
        income = self.screen.calc_gross_income("yearly", ["all"])
        relationship_status = "maried" if self.screen.is_joint() else "single"
        multiplier = 0
        for band in self.income_bands[relationship_status]:
            # if the income is less than the band then set the multiplier and break out of the loop
            if income <= band["max"]:
                multiplier = band["percent"]
                break

        return self.get_variable() * multiplier
