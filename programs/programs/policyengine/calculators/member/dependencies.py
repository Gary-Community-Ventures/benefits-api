from programs.programs.policyengine.calculators.dependencies import Member


class EmploymentIncomeDepnedency(Member):
    field = "employment_income"

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['wages', 'selfEmployment']))


class AgeDependency(Member):
    field = "age"

    def value(self):
        return self.member.age


class PregnancyDependency(Member):
    field = "is_pregnant"

    def value(self):
        return self.member.pregnant


class TaxUnitHeadDependency(Member):
    field = "is_tax_unit_head"

    def value(self):
        return self.screen.get_head().id == self.member.id


class TaxUnitSpouseDependency(Member):
    field = "is_tax_unit_spouse"

    def value(self):
        return self.relationship_map[self.screen.get_head().id] == self.member.id


class TaxUnitDependentDependency(Member):
    field = "is_tax_unit_dependent"

    def value(self):
        is_tax_unit_spouse = TaxUnitSpouseDependency(self.screen, self.member, self.relationship_map)
        is_tax_unit_head = TaxUnitHeadDependency(self.screen, self.member, self.relationship_map)
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
    field = "wic_category"


class Wic(Member):
    field = "wic"


class Medicaid(Member):
    field = "medicaid"


class Ssi(Member):
    field = "ssi"


class SsiEarnedIncomeDependency(Member):
    field = "ssi_earned_income"

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['earned']))


class SsiUnearnedIncomeDependency(Member):
    field = "ssi_unearned_income"

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['unearned']))


class SsiDisabledDependency(Member):
    field = "is_ssi_disabled"

    def value(self):
        return self.member.has_disability()


class SsiCountableResourcesDependency(Member):
    field = "ssi_countable_resources"

    def value(self):
        ssi_assets = 0
        if self.member.age >= 19:
            ssi_assets = self.screen.household_assets / self.screen.num_adults()

        return int(ssi_assets)


class SsiAmountIfEligible(Member):
    field = "ssi_amount_if_eligible"


class Andcs(Member):
    field = "co_state_supplement"


class Oap(Member):
    field = "co_oap"


class PellGrant(Member):
    field = "pell_grant"


class PellGrantDependentAvailableIncomeDependency(Member):
    field = "pell_grant_dependent_available_income"

    def value(self):
        return int(self.member.calc_gross_income('yearly', ['all'])),


class PellGrantCountableAssetsDependency(Member):
    field = "pell_grant_countable_assets"

    def value(self):
        return int(self.screen.household_assets)


class CostOfAttendingCollegeDependency(Member):
    field = "cost_of_attending_college"

    def value(self):
        return 22_288 * (self.member.age >= 16 and self.member.student)


class PellGrantMonthsInSchoolDependency(Member):
    field = "pell_grant_months_in_school"

    def value(self):
        return 9


class ChpEligible(Member):
    field = "co_chp_eligible"
