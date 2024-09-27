from programs.programs.policyengine.calculators.base import PolicyEngineSpmCalulator
import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.policyengine.calculators.dependencies.base import Member, SpmUnit


class Snap(PolicyEngineSpmCalulator):
    pe_name = "snap"
    pe_inputs = [
        dependency.spm.SnapChildSupportDeductionDependency,
        dependency.spm.SnapGrossIncomeDependency,
        dependency.spm.SnapAssetsDependency,
        dependency.spm.MeetsSnapCategoricalEligibilityDependency,
        dependency.spm.SnapEmergencyAllotmentDependency,
        dependency.spm.HousingCostDependency,
        dependency.spm.MeetsSnapGrossIncomeTestDependency,
        dependency.spm.HasPhoneExpenseDependency,
        dependency.spm.HasHeatingCoolingExpenseDependency,
        dependency.spm.HeatingCoolingExpenseDependency,
        dependency.spm.ElectricityExpenseDependency,
        dependency.spm.SnapEarnedIncomeDependency,
        dependency.spm.MeetsSnapAssetTestDependency,
        dependency.spm.SnapDependentCareDeductionDependency,
    ]
    pe_outputs = [dependency.spm.Snap]
    pe_period_month = "01"

    @property
    def pe_output_period(self):
        return self.pe_period + "-" + self.pe_period_month

    def value(self):
        return int(self.sim.value(self.pe_category, self.pe_sub_category, self.pe_name, self.pe_output_period)) * 12


class SchoolLunch(PolicyEngineSpmCalulator):
    pe_name = "school_meal_daily_subsidy"
    pe_inputs = dependency.school_lunch_income
    pe_outputs = [dependency.spm.SchoolMealDailySubsidy, dependency.spm.SchoolMealTier]

    amount = 120

    def value(self):
        total = 0
        num_children = self.screen.num_children(3, 18)

        if self.get_variable() > 0 and num_children > 0:
            if self.sim.value(self.pe_category, self.pe_sub_category, "school_meal_tier", self.pe_period) != "PAID":
                total = SchoolLunch.amount * num_children

        return total


class Tanf(PolicyEngineSpmCalulator):
    pe_name = "co_tanf"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.PregnancyDependency,
        dependency.member.FullTimeCollegeStudentDependency,
        dependency.spm.TanfCountableGrossIncomeDependency,
        dependency.spm.TanfCountableGrossUnearnedIncomeDependency,
        dependency.household.CoStateCode,
    ]
    pe_outputs = [dependency.spm.Tanf]


class Acp(PolicyEngineSpmCalulator):
    pe_name = "acp"
    pe_inputs = [
        dependency.spm.BroadbandCostDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.spm.Acp]


class Lifeline(PolicyEngineSpmCalulator):
    pe_name = "lifeline"
    pe_inputs = [
        dependency.spm.BroadbandCostDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.spm.Lifeline]
