from ..base import UrgentNeedFunction


class MealInCounties(UrgentNeedFunction):
    dependencies = ["county"]
    counties = ["Denver County", "Jefferson County"]

    def eligible(self):
        """
        Household lives in Denver or Jefferson County
        """
        return self.screen.county in self.counties
