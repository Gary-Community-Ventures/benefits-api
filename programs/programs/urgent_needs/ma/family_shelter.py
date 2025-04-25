from ..base import UrgentNeedFunction


class FamilyShelter(UrgentNeedFunction):
    dependencies = ["household_assets", "income_amount", "income_frequency", "age"]
    fpl_percent = 1.15
    asset_limit = 5_000

    def eligible(self):
        """
        Return True if the household is SNAP eligible and lives in Denver
        """
        # income
        income_limit = self.urgent_need.year.as_dict()[self.screen.household_size - 1] * self.fpl_percent
        income = self.screen.calc_gross_income("yearly", ["all"])
        # income
        income_limit = self.urgent_need.year.as_dict()[self.screen.household_size - 1] * self.fpl_percent
        income = self.screen.calc_gross_income("yearly", ["all"])
        income_eligible = income < income_limit

        # assets
        asset_eligible = int(self.screen.household_assets) < self.asset_limit

        # child
        has_child = self.screen.num_children(age_max=20, include_pregnant=True) > 0

        return income_eligible and asset_eligible and has_child
