from .base import SpmUnit


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


class SnapUnearnedIncomeDependency(SpmUnit):
    field = "snap_unearned_income"
    dependencies = (
        "income_type",
        "income_amount",
        "income_frequency",
    )

    def value(self):
        return self.screen.calc_gross_income("yearly", ["unearned"])


class HousingCostDependency(SpmUnit):
    field = "housing_cost"

    def value(self):
        return int(self.screen.calc_expenses("yearly", ["rent", "mortgage", "subsidizedRent"]))


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


class TakesUpSnapIfEligibleDependency(SpmUnit):
    field = "takes_up_snap_if_eligible"

    def value(self):
        return True


class HasHeatingCoolingExpenseDependency(SpmUnit):
    field = "has_heating_cooling_expense"

    def value(self):
        return self.screen.has_expense(["heating", "cooling"])


class HasPhoneExpenseDependency(SpmUnit):
    field = "has_phone_expense"

    def value(self):
        return self.screen.has_expense(["telephone"])


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


class HoaFeesExpenseDependency(SpmUnit):
    field = "homeowners_association_fees"

    def value(self):
        return self.screen.calc_expenses("yearly", ["hoa"])


class HomeownersInsuranceExpenseDependency(SpmUnit):
    field = "homeowners_insurance"

    def value(self):
        return self.screen.calc_expenses("yearly", ["homeownersInsurance"])


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


class MaTafdc(SpmUnit):
    field = "ma_tafdc"


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
        return int(self.screen.calc_gross_income("yearly", ["unearned"], exclude=["cashAssistance"]))


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
        return int(
            self.screen.calc_gross_income(
                "yearly", ["unearned"], exclude=["sSI", "gifts", "cashAssistance", "cOSDisability"]
            )
        )


class PreSubsidyChildcareExpensesDependency(SpmUnit):
    field = "spm_unit_pre_subsidy_childcare_expenses"

    def value(self):
        return self.screen.calc_expenses("yearly", ["childCare", "dependentCare"])


class NcScca(SpmUnit):
    field = "nc_scca"


class NcSccaCountableIncomeDependency(SpmUnit):
    field = "nc_scca_countable_income"
    income_types = [
        "wages",
        "selfEmployment",
        "pension",
        "veteran",
        "unemployment",
        "sSDisability",
        "workersComp",
        "sSRetirement",
        "deferredComp",
        "rental",
        "childSupport",
        "alimony",
        "investment",
        "sSSurvivor",
        "sSDependent",
        "boarder",
    ]

    def value(self):
        return self.screen.calc_gross_income("yearly", self.income_types)


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


class AssetsDependency(SpmUnit):
    field = "spm_unit_assets"

    def value(self):
        assets = self.screen.household_assets or 0
        return int(assets)


class MaEaedc(SpmUnit):
    field = "ma_eaedc"


# NOTE: PE has an open issue to calculate this: https://github.com/PolicyEngine/policyengine-us/issues/5768
class MaEaedcLivingArangementDependency(SpmUnit):
    field = "ma_eaedc_living_arrangement"

    def value(self):
        return "A"


class MaEaedc(SpmUnit):
    field = "ma_eaedc"


class CashAssetsDependency(SpmUnit):
    field = "spm_unit_cash_assets"

    def value(self):
        assets = self.screen.household_assets or 0
        return int(assets)
