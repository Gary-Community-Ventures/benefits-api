from .base import Member


class AgeDependency(Member):
    field = 'age'
    dependencies = ('age',)

    def value(self):
        return self.member.age


class PregnancyDependency(Member):
    field = 'is_pregnant'

    def value(self):
        return self.member.pregnant or False


class FullTimeCollegeStudentDependency(Member):
    field = 'is_full_time_college_student'

    def value(self):
        return self.member.student or False


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
        is_tax_unit_spouse = TaxUnitSpouseDependency(
            self.screen, self.member, self.relationship_map
        ).value()
        is_tax_unit_head = TaxUnitHeadDependency(
            self.screen, self.member, self.relationship_map
        ).value()
        is_tax_unit_dependent = (
            (
                self.member.age <= 18
                or (self.member.student and self.member.age <= 23)
                or self.member.has_disability()
            )
            and (
                self.member.calc_gross_income('yearly', ['all'])
                < self.screen.calc_gross_income('yearly', ['all']) / 2
            )
            and (not (is_tax_unit_head or is_tax_unit_spouse))
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


class IncomeDependency(Member):
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )
    income_types = []

    def value(self):
        return int(self.member.calc_gross_income('yearly', self.income_types))


class EmploymentIncomeDependency(IncomeDependency):
    field = 'employment_income'
    income_types = ['wages']


class SelfEmploymentIncomeDependency(IncomeDependency):
    field = 'self_employment_income'
    income_types = ['selfEmployment']


class RentalIncomeDependency(IncomeDependency):
    field = 'rental_income'
    income_types = ['rental']


class PensionIncomeDependency(IncomeDependency):
    field = 'taxable_pension_income'
    income_types = ['pension', 'veteran']


class SocialSecurityIncomeDependency(IncomeDependency):
    field = 'social_security'
    income_types = ['sSDisability', 'sSSurvivor', 'sSRetirement', 'sSDependent']


class SsiEarnedIncomeDependency(IncomeDependency):
    field = 'ssi_earned_income'
    income_types = ['earned']


class SsiUnearnedIncomeDependency(IncomeDependency):
    field = 'ssi_unearned_income'
    income_types = ['unearned']
