from .base import SpmUnit
from programs.models import FederalPoveryLimit


class SnapChildSupportDeductionDependency(SpmUnit):
    field = "snap_child_support_deduction"

    def value(self):
        return self.screen.calc_expenses("yearly", ["childSupport"])


class SnapDependentCareDeductionDependency(SpmUnit):
    field = "childcare_expenses"

    def value(self):
        return self.screen.calc_expenses("yearly", ["childCare"])


class SnapEarnedIncomeDependency(SpmUnit):
    field = "snap_earned_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return self.screen.calc_gross_income("yearly", ["earned"])


class HousingCostDependency(SpmUnit):
    field = "housing_cost"

    def value(self):
        return int(self.screen.calc_expenses("yearly", ["rent", "mortgage"]))


class SnapAssetsDependency(SpmUnit):
    field = "snap_assets"

    def value(self):
        assets = self.screen.household_assets or 0
        return int(assets)


class SnapGrossIncomeDependency(SpmUnit):
    field = "snap_gross_income"
    dependencies = (
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return int(self.screen.calc_gross_income("yearly", ["all"]))


class MeetsSnapGrossIncomeTestDependency(SpmUnit):
    field = "meets_snap_gross_income_test"
    dependencies = (
        "income_amount",
        "income_frequency",
        "household_size",
    )

    def value(self):
        fpl = FederalPoveryLimit.objects.get(year="THIS YEAR").as_dict()
        snap_gross_income = self.screen.calc_gross_income("yearly", ["all"])
        snap_gross_limit = 2 * fpl[self.screen.household_size]

        return snap_gross_income < snap_gross_limit


class MeetsSnapAssetTestDependency(SpmUnit):
    field = "meets_snap_asset_test"

    def value(self):
        return True


class MeetsSnapCategoricalEligibilityDependency(SpmUnit):
    field = "meets_snap_categorical_eligibility"

    def value(self):
        return False


class HasHeatingCoolingExpenseDependency(SpmUnit):
    field = "has_heating_cooling_expense"

    def value(self):
        return self.screen.has_expense(["heating", "cooling"])


class HasPhoneExpenseDependency(SpmUnit):
    field = "has_phone_expense"

    def value(self):
        return self.screen.has_expense(["telephone"])


class HasUsdaElderlyDisabledDependency(SpmUnit):
    field = "has_usda_elderly_disabled"

    def value(self):
        return any(member.is_elderly() or member.has_disability() for member in self.members)


class UtilityExpenseDependency(SpmUnit):
    field = "utility_expense"

    def value(self):
        return int(self.screen.calc_expenses("yearly", ["otherUtilities", "heating", "cooling"]))


class HeatingCoolingExpenseDependency(SpmUnit):
    field = "heating_cooling_expense"

    def value(self):
        return self.screen.calc_expenses("yearly", ["heating", "cooling"])


class PhoneExpenseDependency(SpmUnit):
    field = "phone_expense"

    def value(self):
        return self.screen.calc_expenses("yearly", ["telephone"])


class ElectricityExpenseDependency(SpmUnit):
    field = "electricity_expense"

    def value(self):
        return self.screen.calc_expenses("yearly", ["otherUtilities"])


class WaterExpenseDependency(SpmUnit):
    field = "water_expense"

    def value(self):
        return self.screen.calc_expenses("yearly", ["otherUtilities"])


class SnapEmergencyAllotmentDependency(SpmUnit):
    field = "snap_emergency_allotment"

    def value(self):
        return 0


class Snap(SpmUnit):
    field = "snap"


class Acp(SpmUnit):
    field = "acp"


class SchoolMealDailySubsidy(SpmUnit):
    field = "school_meal_daily_subsidy"


class SchoolMealTier(SpmUnit):
    field = "school_meal_tier"


class Lifeline(SpmUnit):
    field = "lifeline"


class Tanf(SpmUnit):
    field = "tanf"


class CoTanf(SpmUnit):
    field = "co_tanf"


class NcTanf(SpmUnit):
    field = "nc_tanf"


class CoTanfCountableGrossIncomeDependency(SpmUnit):
    field = "co_tanf_countable_gross_earned_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return int(self.screen.calc_gross_income("yearly", ["earned"]))


class CoTanfCountableGrossUnearnedIncomeDependency(SpmUnit):
    field = "co_tanf_countable_gross_unearned_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return int(self.screen.calc_gross_income("yearly", ["unearned"]))


class NcTanfCountableEarnedIncomeDependency(SpmUnit):
    field = "nc_tanf_countable_earned_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return int(self.screen.calc_gross_income("yearly", ["earned"]))


class NcTanfCountableGrossUnearnedIncomeDependency(SpmUnit):
    field = "nc_tanf_countable_gross_unearned_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return int(self.screen.calc_gross_income("yearly", ["unearned"]))


class BroadbandCostDependency(SpmUnit):
    field = "broadband_cost"

    def value(self):
        return 500


class SchoolMealCountableIncomeDependency(SpmUnit):
    field = "school_meal_countable_income"
    income_types = [
        "wages",
        "selfEmployment",
        "rental",
        "pension",
        "veteran",
        "sSDisability",
        "sSSurvivor",
        "sSRetirement",
        "sSDependent",
    ]

    def value(self):
        return self.screen.calc_gross_income("yearly", self.income_types)
