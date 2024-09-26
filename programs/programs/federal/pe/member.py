from programs.programs.policyengine.calculators.base import PolicyEngineMembersCalculator
import programs.programs.policyengine.calculators.dependencies as dependency
from screener.models import HouseholdMember


class Wic(PolicyEngineMembersCalculator):
    wic_categories = {
        "NONE": 0,
        "INFANT": 0,
        "CHILD": 0,
        "PREGNANT": 0,
        "POSTPARTUM": 0,
        "BREASTFEEDING": 0,
    }
    pe_name = "wic"
    pe_inputs = [
        dependency.member.PregnancyDependency,
        dependency.member.AgeDependency,
        *dependency.school_lunch_income,
    ]
    pe_outputs = [dependency.member.Wic, dependency.member.WicCategory]

    def member_value(self, member: HouseholdMember):
        if self.get_member_variable(member.id) <= 0:
            return 0

        wic_category = self.sim.value("people", str(member.id), "wic_category", self.pe_period)
        return self.wic_categories[wic_category] * 12


class Medicaid(PolicyEngineMembersCalculator):
    pe_name = "medicaid"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.PregnancyDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [
        dependency.member.AgeDependency,
        dependency.member.Medicaid,
    ]

    child_medicaid_average = 0
    adult_medicaid_average = 0
    aged_medicaid_average = 0

    presumptive_amount = 74 * 12

    def _value_by_age(self, age: int):
        # here we need to adjust for children as policy engine
        # just uses the average which skews very high for adults and
        # aged adults

        if age <= 18:
            medicaid_estimated_value = self.child_medicaid_average
        elif age > 18 and age < 65:
            medicaid_estimated_value = self.adult_medicaid_average
        elif age >= 65:
            medicaid_estimated_value = self.aged_medicaid_average
        else:
            medicaid_estimated_value = 0

        return medicaid_estimated_value

    def member_value(self, member: HouseholdMember):
        if self.get_member_variable(member.id) <= 0:
            return 0

        # here we need to adjust for children as policy engine
        # just uses the average which skews very high for adults and
        # aged adults

        if self._get_age(member.id) <= 18:
            return self.child_medicaid_average
        elif self._get_age(member.id) > 18 and self._get_age(member.id) < 65:
            return self.adult_medicaid_average
        elif self._get_age(member.id) >= 65:
            return self.aged_medicaid_average

        return 0

    def _get_age(self, member_id: int) -> int:
        return self.sim.value(self.pe_category, str(member_id), "age", self.pe_period)


class PellGrant(PolicyEngineMembersCalculator):
    pe_name = "pell_grant"
    pe_inputs = [
        dependency.member.PellGrantDependentAvailableIncomeDependency,
        dependency.member.PellGrantCountableAssetsDependency,
        dependency.member.CostOfAttendingCollegeDependency,
        dependency.member.PellGrantMonthsInSchoolDependency,
        dependency.tax.PellGrantPrimaryIncomeDependency,
        dependency.tax.PellGrantDependentsInCollegeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.TaxUnitHeadDependency,
        dependency.member.TaxUnitSpouseDependency,
    ]
    pe_outputs = [dependency.member.PellGrant]


class Ssi(PolicyEngineMembersCalculator):
    pe_name = "ssi"
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
    pe_outputs = [dependency.member.Ssi]
