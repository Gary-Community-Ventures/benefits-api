from ..base import PolicyEnigineCalulator
import programs.programs.policyengine.calculators.dependencies as dependency


class PolicyEngineSpmCalulator(PolicyEnigineCalulator):
    pe_category = 'spm_units'
    pe_sub_category = 'spm_unit'


class Snap(PolicyEngineSpmCalulator):
    pe_name = 'snap'
    pe_inputs = [
        dependency.spm.SnapChildSupportDeductionDependency,
        dependency.spm.SnapGrossIncomeDependency,
        dependency.spm.SnapAssetsDependency,
        dependency.spm.MeetsSnapCategoricalEligibilityDependency,
        dependency.spm.SnapEmergencyAllotmentDependency,
    ]
    pe_outputs = [dependency.spm.Snap]

    def value(self):
        return self.get_data()[self.pe_name][self.pe_period]


class SchoolLunch(PolicyEngineSpmCalulator):
    pe_name = 'school_meal_daily_subsidy'
    pe_inputs = [dependency.member.EmploymentIncomeDependency]
    pe_outputs = [dependency.spm.SchoolMealDailySubsidy, dependency.spm.SchoolMealTier]

    def value(self):
        total = 0
        num_children = self.screen.num_children(3, 18)

        if self.get_data()[self.pe_name][self.pe_period] > 0 and num_children > 0:
            if self.get_data()['school_meal_tier'][self.pe_period] != 'PAID':
                total = 680 * num_children

        return total


class Tanf(PolicyEngineSpmCalulator):
    pe_name = 'co_tanf'
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.PregnancyDependency,
        dependency.member.EmploymentIncomeDependency
    ]
    pe_outputs = [dependency.spm.Tanf]


class Acp(PolicyEngineSpmCalulator):
    pe_name = 'acp'
    pe_inputs = [
        dependency.member.EmploymentIncomeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.spm.BroadbandCostDependency,
    ]
    pe_outputs = [dependency.spm.Acp]


class Lifeline(PolicyEngineSpmCalulator):
    pe_name = 'lifeline'
