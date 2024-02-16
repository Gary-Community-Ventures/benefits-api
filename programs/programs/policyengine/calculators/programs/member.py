from ..base import PolicyEnigineCalulator
import programs.programs.policyengine.calculators.dependencies as dependency


class PolicyEngineMembersCalculator(PolicyEnigineCalulator):
    tax_dependent = True
    pe_category = 'people'

    def value(self):
        total = 0
        for member in self.screen.household_members.all():
            # The following programs use income from the tax unit,
            # so we want to skip any members that are not in the tax unit.
            if not self.in_tax_unit(member.id) and self.tax_dependent:
                continue

            pe_value = self.get_variable(member.id)

            total += pe_value

        return total

    def in_tax_unit(self, member_id: int) -> bool:
        return str(member_id) in self.sim.members('tax_units', 'tax_unit')

    def get_variable(self, member_id: int):
        return self.sim.value(self.pe_category, str(member_id), self.pe_name, self.pe_period)


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

        for member in self.screen.household_members.all():
            if self.get_variable(member.id) > 0:
                wic_category = self.sim.value('people', str(member.id), 'wic_category', self.pe_period)
                total += self.wic_categories[wic_category] * 12

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

        members = self.screen.household_members.all()

        for member in members:
            if self.get_variable(member.id) <= 0:
                continue

            # here we need to adjust for children as policy engine
            # just uses the average which skews very high for adults and
            # aged adults

            if self._get_age(member.id) <= 18:
                medicaid_estimated_value = self.co_child_medicaid_average
            elif self._get_age(member.id) > 18 and self._get_age(member.id) < 65:
                medicaid_estimated_value = self.co_adult_medicaid_average
            elif self._get_age(member.id) >= 65:
                medicaid_estimated_value = self.co_aged_medicaid_average
            else:
                medicaid_estimated_value = 0

            total += medicaid_estimated_value

        in_wic_demographic = False
        for member in members:
            if member.pregnant is True or member.age <= 5:
                in_wic_demographic = True
        if total == 0 and in_wic_demographic:
            if self.screen.has_benefit('medicaid') is True \
                    or self.screen.has_benefit('tanf') is True \
                    or self.screen.has_benefit('snap') is True:
                total = self.presumptive_amount

        return total

    def _get_age(self, member_id: int) -> int:
        return self.sim.value(self.pe_category, str(member_id), 'age', self.pe_period)


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

        for member in self.screen.household_members.all():
            chp_eligible = self.sim.value(self.pe_category, str(member.id), 'co_chp_eligible', self.pe_period)
            if chp_eligible > 0 and self.screen.has_insurance_types(('none',)):
                total += self.amount

        return total
