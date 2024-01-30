from ..base import PolicyEnigineCalulator
from ..constants import PREVIOUS_YEAR
import programs.programs.policyengine.calculators.dependencies as dependency


class PolicyEngineTaxUnitCalulator(PolicyEnigineCalulator):
    pe_category = 'tax_units'
    pe_sub_category = 'tax_unit'
    pe_period = PREVIOUS_YEAR


class Eitc(PolicyEngineTaxUnitCalulator):
    pe_name = 'eitc'
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.EmploymentIncomeDependency,
        dependency.member.SelfEmploymentIncomeDependency,
        dependency.member.InvestmentIncomeDependency,
        dependency.member.RentalIncomeDependency,
        dependency.member.PensionIncomeDependency,
        dependency.member.SocialSecurityIncomeDependency,
    ]
    pe_outputs = [dependency.tax.Eitc]


class Coeitc(PolicyEngineTaxUnitCalulator):
    pe_name = 'co_eitc'
    pe_inputs = Eitc.pe_inputs
    pe_outputs = [dependency.tax.Coeitc]


class Ctc(PolicyEngineTaxUnitCalulator):
    pe_name = 'ctc'
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.EmploymentIncomeDependency,
        dependency.member.SelfEmploymentIncomeDependency,
        dependency.member.InvestmentIncomeDependency,
        dependency.member.RentalIncomeDependency,
        dependency.member.PensionIncomeDependency,
        dependency.member.SocialSecurityIncomeDependency,
    ]
    pe_outputs = [dependency.tax.Ctc]


class Coctc(PolicyEngineTaxUnitCalulator):
    pe_name = 'ctc'
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.EmploymentIncomeDependency,
    ]
    pe_outputs = [dependency.tax.Ctc]

    income_bands = {
        "single": [{"max": 25000, "percent": .6}, {"max": 50000, "percent": .3}, {"max": 75000, "percent": .1}],
        "maried": [{"max": 35000, "percent": .6}, {"max": 60000, "percent": .3}, {"max": 85000, "percent": .1}]
    }

    def value(self):
        income = self.screen.calc_gross_income('yearly', ['all'])
        relationship_status = 'maried' if self.screen.is_joint() else 'single'
        multiplier = 0
        for band in self.income_bands[relationship_status]:
            # if the income is less than the band then set the multiplier and break out of the loop
            if income <= band['max']:
                multiplier = band['percent']
                break

        return self.get_data()[self.pe_name][self.pe_period] * multiplier
