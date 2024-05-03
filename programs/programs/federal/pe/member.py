from programs.programs.policyengine.calculators.base import PolicyEngineMembersCalculator
import programs.programs.policyengine.calculators.dependencies as dependency


class Wic(PolicyEngineMembersCalculator):
    wic_categories = {
        'NONE': 0,
        'INFANT': 130,
        'CHILD': 74,
        "PREGNANT": 100,
        "POSTPARTUM": 100,
        "BREASTFEEDING": 100,
    }
    pe_name = 'wic'
    pe_inputs = [
        dependency.member.PregnancyDependency,
        dependency.member.AgeDependency,
        *dependency.school_lunch_income,
    ]
    pe_outputs = [dependency.member.Wic, dependency.member.WicCategory]

    def value(self):
        total = 0

        for _, pvalue in self.get_data().items():
            if pvalue[self.pe_name][self.pe_period] > 0:
                total += self.wic_categories[pvalue['wic_category'][self.pe_period]] * 12

        return total


class Medicaid(PolicyEngineMembersCalculator):
    pe_name = 'medicaid'
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

    def value(self):
        total = 0

        for _, pvalue in self.get_data().items():
            if pvalue[self.pe_name][self.pe_period] <= 0:
                continue

            total += self._value_by_age(pvalue['age'][self.pe_period])

        in_wic_demographic = False
        for member in self.screen.household_members.all():
            if member.pregnant is True or member.age <= 5:
                in_wic_demographic = True
        if total == 0 and in_wic_demographic:
            if self.screen.has_benefit('medicaid') is True \
                    or self.screen.has_benefit('tanf') is True \
                    or self.screen.has_benefit('snap') is True:
                total = self.presumptive_amount

        return total


class PellGrant(PolicyEngineMembersCalculator):
    pe_name = 'pell_grant'
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
    pe_name = 'ssi'
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

