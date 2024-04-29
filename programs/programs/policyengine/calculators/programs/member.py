from ..base import PolicyEnigineCalulator
import programs.programs.policyengine.calculators.dependencies as dependency


class PolicyEngineMembersCalculator(PolicyEnigineCalulator):
    tax_dependent = True
    pe_category = 'people'

    def value(self):
        total = 0
        for pkey, pvalue in self.get_data().items():
            # The following programs use income from the tax unit,
            # so we want to skip any members that are not in the tax unit.
            if not self.in_tax_unit(pkey) and self.tax_dependent:
                continue

            pe_value = pvalue[self.pe_name][self.pe_period]

            total += pe_value

        return total

    def in_tax_unit(self, member_id) -> bool:
        return str(member_id) in self.pe_data['tax_units']['tax_unit']['members']

    def get_data(self):
        return self.pe_data[self.pe_category]


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

    co_child_medicaid_average = 200 * 12
    co_adult_medicaid_average = 310 * 12
    co_aged_medicaid_average = 170 * 12

    presumptive_amount = 74 * 12

    def value(self):
        total = 0

        for _, pvalue in self.get_data().items():
            if pvalue[self.pe_name][self.pe_period] <= 0:
                continue

            # here we need to adjust for children as policy engine
            # just uses the average which skews very high for adults and
            # aged adults

            if pvalue['age'][self.pe_period] <= 18:
                medicaid_estimated_value = self.co_child_medicaid_average
            elif pvalue['age'][self.pe_period] > 18 and pvalue['age'][self.pe_period] < 65:
                medicaid_estimated_value = self.co_adult_medicaid_average
            elif pvalue['age'][self.pe_period] >= 65:
                medicaid_estimated_value = self.co_aged_medicaid_average
            else:
                medicaid_estimated_value = 0

            total += medicaid_estimated_value

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
