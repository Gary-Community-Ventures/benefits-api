from programs.programs.helpers import snap_ineligible_student
from .base import Member


class AgeDependency(Member):
    field = "age"
    dependencies = ("age",)

    def value(self):
        return self.member.age


class PregnancyDependency(Member):
    field = "is_pregnant"

    def value(self):
        return self.member.pregnant or False


class ExpectedChildrenPregnancyDependency(Member):
    field = "current_pregnancies"

    def value(self):
        return 1 if self.member.pregnant else 0


class FullTimeCollegeStudentDependency(Member):
    field = "is_full_time_college_student"

    def value(self):
        return self.member.student or False


class TaxUnitHeadDependency(Member):
    field = "is_tax_unit_head"
    dependencies = ("relationship",)

    def value(self):
        if self.member.is_head():
            return True

        other_unit = self.screen.other_tax_unit_structure()

        if other_unit["head"] is None:
            return False

        return other_unit["head"].id == self.member.id


class TaxUnitSpouseDependency(Member):
    field = "is_tax_unit_spouse"
    dependencies = ("relationship",)

    def value(self):
        if self.member.is_spouse():
            return True

        other_unit = self.screen.other_tax_unit_structure()

        if other_unit["spouse"] is None:
            return False

        return other_unit["spouse"].id == self.member.id


class TaxUnitDependentDependency(Member):
    field = "is_tax_unit_dependent"
    dependencies = (
        "relationship",
        "age",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        if self.member.is_dependent():
            return True

        other_unit = self.screen.other_tax_unit_structure()

        for member in other_unit["dependents"]:
            if member.id == self.member.id:
                return True

        return False


class WicCategory(Member):
    field = "wic_category"


class MedicaidCategory(Member):
    field = "medicaid_category"


class MedicaidSeniorOrDisabled(Member):
    field = "is_optional_senior_or_disabled_for_medicaid"


class Wic(Member):
    field = "wic"


class Medicaid(Member):
    field = "medicaid"


class Ssi(Member):
    field = "ssi"


class IsDisabledDependency(Member):
    field = "is_disabled"

    def value(self):
        return self.member.disabled or self.member.long_term_disability


# The Member class runs once per each household member, to ensure that the medical expenses
# are only counted once and only if a member is elderly or disabled; the medical expense is divided
# by the total number of elderly or disabled members.
class MedicalExpenseDependency(Member):
    field = "medical_out_of_pocket_expenses"

    def value(self):
        elderly_or_disabled_members = [
            member for member in self.screen.household_members.all() if member.age >= 60 or member.has_disability()
        ]
        count_of_elderly_or_disabled_members = len(elderly_or_disabled_members)

        if self.member.age >= 60 or self.member.has_disability():
            return self.screen.calc_expenses("yearly", ["medical"]) / count_of_elderly_or_disabled_members

        return 0


class PropertyTaxExpenseDependency(Member):
    field = "real_estate_taxes"

    def value(self):
        if self.member.age >= 18:
            return self.screen.calc_expenses("yearly", ["propertyTax"]) / self.screen.num_adults(18)

        return 0


class IsBlindDependency(Member):
    field = "is_blind"

    def value(self):
        return self.member.visually_impaired


class SsiReportedDependency(Member):
    field = "ssi_reported"

    def value(self):
        # Policy Engine uses this value for is_ssi_disabled, but it does not apply to MFB
        return 0


class SsiCountableResourcesDependency(Member):
    field = "ssi_countable_resources"
    dependencies = (
        "household_assets",
        "age",
    )

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


class FamilyAffordabilityTaxCredit(Member):
    field = "co_family_affordability_credit"


class PellGrant(Member):
    field = "pell_grant"


class PellGrantDependentAvailableIncomeDependency(Member):
    field = "pell_grant_dependent_available_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return int(self.member.calc_gross_income("yearly", ["all"]))


class PellGrantCountableAssetsDependency(Member):
    field = "pell_grant_countable_assets"
    dependencies = ("household_assets",)

    def value(self):
        return int(self.screen.household_assets)


class CostOfAttendingCollegeDependency(Member):
    field = "cost_of_attending_college"
    dependencies = ("age",)

    def value(self):
        return 22_288 * (self.member.age >= 16 and self.member.student)


class PellGrantMonthsInSchoolDependency(Member):
    field = "pell_grant_months_in_school"

    def value(self):
        return 9


class ChpEligible(Member):
    field = "co_chp_eligible"


class CommoditySupplementalFoodProgram(Member):
    field = "commodity_supplemental_food_program"


class SnapIneligibleStudentDependency(Member):
    field = "is_snap_ineligible_student"

    dependencies = ("age",)

    # PE does not take the age of the children into acount, so we calculate this ourselves
    def value(self):
        return snap_ineligible_student(self.screen, self.member)


class IncomeDependency(Member):
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )
    income_types = []

    def value(self):
        return int(self.member.calc_gross_income("yearly", self.income_types))


class EmploymentIncomeDependency(IncomeDependency):
    field = "employment_income"
    income_types = ["wages"]


class SelfEmploymentIncomeDependency(IncomeDependency):
    field = "self_employment_income"
    income_types = ["selfEmployment"]


class RentalIncomeDependency(IncomeDependency):
    field = "rental_income"
    income_types = ["rental"]


class PensionIncomeDependency(IncomeDependency):
    field = "taxable_pension_income"
    income_types = ["pension", "veteran"]


class SocialSecurityIncomeDependency(IncomeDependency):
    field = "social_security"
    income_types = ["sSDisability", "sSSurvivor", "sSRetirement", "sSDependent"]


class SsiEarnedIncomeDependency(IncomeDependency):
    field = "ssi_earned_income"
    income_types = ["earned"]


class SsiUnearnedIncomeDependency(IncomeDependency):
    field = "ssi_unearned_income"
    income_types = ["unearned"]
