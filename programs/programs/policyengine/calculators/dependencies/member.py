from .base import Member


class EmploymentIncomeDependency(Member):
    field = 'employment_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['wages']))


class SelfEmploymentIncomeDependency(Member):
    field = 'self_employment_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['selfEmployment']))


class AgeDependency(Member):
    field = 'age'
    dependencies = ('age',)

    def value(self):
        return self.member.age


class PregnancyDependency(Member):
    field = 'is_pregnant'

    def value(self):
        return self.member.pregnant or False


class TaxUnitHeadDependency(Member):
    field = 'is_tax_unit_head'
    dependencies = ('relationship',)

    def value(self):
        return self.screen.get_head().id == self.member.id


class TaxUnitSpouseDependency(Member):
    field = 'is_tax_unit_spouse'
    dependencies = ('relationship',)

    def value(self):
        return self.relationship_map[self.screen.get_head().id] == self.member.id


class TaxUnitDependentDependency(Member):
    field = 'is_tax_unit_dependent'
    dependencies = (
        'relationship',
        'age',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        is_tax_unit_spouse = TaxUnitSpouseDependency(self.screen, self.member, self.relationship_map).value()
        is_tax_unit_head = TaxUnitHeadDependency(self.screen, self.member, self.relationship_map).value()
        is_tax_unit_dependent = (
            self.member.age <= 18 or
            (self.member.student and self.member.age <= 23) or
            self.member.has_disability()
        ) and (
            self.member.calc_gross_income('yearly', ['all']) < self.screen.calc_gross_income('yearly', ['all']) / 2
        ) and (
            not (is_tax_unit_head or is_tax_unit_spouse)
        )

        return is_tax_unit_dependent


class WicCategory(Member):
    field = 'wic_category'


class Wic(Member):
    field = 'wic'


class Medicaid(Member):
    field = 'medicaid'


class Ssi(Member):
    field = 'ssi'


class SsiEarnedIncomeDependency(Member):
    field = 'ssi_earned_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['earned']))


class SsiUnearnedIncomeDependency(Member):
    field = 'ssi_unearned_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['unearned']))


class IsDisabledDependency(Member):
    field = 'is_disabled'

    def value(self):
        return self.member.disabled or self.member.long_term_disability


class IsBlindDependency(Member):
    field = 'is_blind'

    def value(self):
        return self.member.visually_impaired


class SsiReportedDependency(Member):
    field = 'ssi_reported'

    def value(self):
        # Policy Eninge uses this value for is_ssi_disabled, but it does not apply to MFB
        return 0


class SsiCountableResourcesDependency(Member):
    field = 'ssi_countable_resources'
    dependencies = (
        'household_assets',
        'age',
    )

    def value(self):
        ssi_assets = 0
        if self.member.age >= 19:
            ssi_assets = self.screen.household_assets / self.screen.num_adults()

        return int(ssi_assets)


class SsiAmountIfEligible(Member):
    field = 'ssi_amount_if_eligible'


class Andcs(Member):
    field = 'co_state_supplement'


class Oap(Member):
    field = 'co_oap'


class PellGrant(Member):
    field = 'pell_grant'


class PellGrantDependentAvailableIncomeDependency(Member):
    field = 'pell_grant_dependent_available_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['all']))


class PellGrantCountableAssetsDependency(Member):
    field = 'pell_grant_countable_assets'
    dependencies = ('household_assets',)

    def value(self):
        return int(self.screen.household_assets)


class CostOfAttendingCollegeDependency(Member):
    field = 'cost_of_attending_college'
    dependencies = ('age',)

    def value(self):
        return 22_288 * (self.member.age >= 16 and self.member.student)


class PellGrantMonthsInSchoolDependency(Member):
    field = 'pell_grant_months_in_school'

    def value(self):
        return 9


class ChpEligible(Member):
    field = 'co_chp_eligible'
