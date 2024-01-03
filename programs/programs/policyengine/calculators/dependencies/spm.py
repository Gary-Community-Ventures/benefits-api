from .base import SpmUnit
from programs.models import FederalPoveryLimit


class SnapChildSupportDeductionDependency(SpmUnit):
    field = 'snap_child_support_deduction'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return self.screen.calc_expenses('yearly', ['childSupport'])


class SnapEarnedIncomeDependency(SpmUnit):
    field = 'snap_earned_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return self.screen.calc_gross_income('yearly', ['earned'])


class HousingCostDependency(SpmUnit):
    field = 'housing_cost'
    dependencies = (
        'expense_type',
        'expense_amount',
    )

    def value(self):
        return int(self.screen.calc_expenses('yearly', ['rent', 'mortgage']))


class SnapAssetsDependency(SpmUnit):
    field = 'snap_assets'
    dependencies = ('household_assets',)

    def value(self):
        return int(self.screen.household_assets)


class SnapGrossIncomeDependency(SpmUnit):
    field = 'snap_gross_income'
    dependencies = (
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.screen.calc_gross_income('yearly', ['all']))


class MeetsSnapGrossIncomeTestDependency(SpmUnit):
    field = 'meets_snap_gross_income_test'
    dependencies = (
        'income_amount',
        'income_frequency',
    )

    def value(self):
        fpl = FederalPoveryLimit.objects.get(year='THIS YEAR').as_dict()
        snap_gross_income = self.screen.calc_gross_income('yearly', ['all'])
        snap_gross_limit = 2 * fpl[self.screen.household_size]

        return snap_gross_income < snap_gross_limit


class MeetsSnapAssetTestDependency(SpmUnit):
    field = 'meets_snap_asset_test'

    def value(self):
        return True


class MeetsSnapCategoricalEligibilityDependency(SpmUnit):
    field = 'meets_snap_categorical_eligibility'

    def value(self):
        return False


class HasHeatingCoolingExpenseDependency(SpmUnit):
    field = 'has_heating_cooling_expense'
    dependencies = (
        'expense_type',
        'expense_amount',
    )

    def value(self):
        return self.screen.has_expense(['heating', 'cooling'])


class HasPhoneExpenseDependency(SpmUnit):
    field = 'has_phone_expense'
    dependencies = (
        'expense_type',
        'expense_amount',
    )

    def value(self):
        return self.screen.has_expense(['telephone'])


class UtilityExpenseDependency(SpmUnit):
    field = 'utility_expense'
    dependencies = (
        'expense_type',
        'expense_amount',
    )

    def value(self):
        return int(
            self.screen.calc_expenses(
                'yearly', ['otherUtilities', 'heating', 'cooling']
            )
        )


class SnapEmergencyAllotmentDependency(SpmUnit):
    field = 'snap_emergency_allotment'

    def value(self):
        return 0


class Snap(SpmUnit):
    field = 'snap'


class Acp(SpmUnit):
    field = 'acp'


class SchoolMealDailySubsidy(SpmUnit):
    field = 'school_meal_daily_subsidy'


class SchoolMealTier(SpmUnit):
    field = 'school_meal_tier'


class Lifeline(SpmUnit):
    field = 'lifeline'


class TanfCountableGrossIncomeDependency(SpmUnit):
    field = 'co_tanf_countable_gross_earned_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.screen.calc_gross_income('yearly'['earned']))


class TanfCountableGrossUnearnedIncomeDependency(SpmUnit):
    field = 'co_tanf_countable_gross_unearned_income'
    dependencies = (
        'income_type',
        'income_amount',
        'income_frequency',
    )

    def value(self):
        return int(self.screen.calc_gross_income('yearly'['unearned']))


class Tanf(SpmUnit):
    field = 'co_tanf'


class TanfGrantStandard(SpmUnit):
    field = 'co_tanf_grant_standard'


class BroadbandCostDependency(SpmUnit):
    field = 'broadband_cost'

    def value(self):
        return 500
