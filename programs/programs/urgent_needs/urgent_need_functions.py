from screener.models import Screen
from programs.models import FederalPoveryLimit
from programs.util import Dependencies
from integrations.services.sheets import GoogleSheetsCache


class UrgentNeedFunction:
    """
    Base class for all urgent need conditions
    """

    dependencies = []

    @classmethod
    def calc(cls, screen: Screen, missing_dependencies: Dependencies):
        """
        Calculate if the urgent need can be calculated and if the condition is met
        """
        if not cls.can_calc(missing_dependencies):
            return False

        return cls.eligible(screen)

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Returns if the condition is met
        """
        return True

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        """
        Returns if the condition can be calculated
        """
        if missing_dependencies.has(*cls.dependencies):
            return False

        return True


class ChildAgeFunction(UrgentNeedFunction):
    dependencies = ["age"]
    min_age = 0
    max_age = 18

    @classmethod
    def eligible(cls, screen: Screen):
        """
        return True if the child is between the ages of min_age and max_age
        """
        return screen.num_children(age_min=cls.min_age, age_max=cls.max_age) > 0


class LivesInDenver(UrgentNeedFunction):
    dependencies = ["county"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Household lives in the Denver County
        """
        return screen.county == "Denver County"


class MealInCounties(UrgentNeedFunction):
    dependencies = ["county"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Household lives in Denver or Jefferson County
        """
        eligible_counties = ["Denver County", "Jefferson County"]
        return screen.county in eligible_counties


class HelpkitchenZipcode(UrgentNeedFunction):
    dependencies = ["zipcode"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Lives in a zipcode that is eligible for HelpKitchen
        """
        zipcodes = [
            "80010",
            "80011",
            "80012",
            "80013",
            "80014",
            "80015",
            "80016",
            "80017",
            "80018",
            "80019",
            "80045",
            "80102",
            "80112",
            "80137",
            "80138",
            "80230",
            "80231",
            "80238",
            "80247",
            "80249",
        ]
        return screen.zipcode in zipcodes


class Child(ChildAgeFunction):
    pass


class BiaFoodDelivery(UrgentNeedFunction):
    dependencies = ["county"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if in Adams, Arapahoe, Denver or Jefferson county
        """
        eligible_counties = [
            "Adams County",
            "Arapahoe County",
            "Denver County",
            "Jefferson County",
        ]
        return screen.county in eligible_counties


class Trua(UrgentNeedFunction):
    dependencies = ["household_size", "income_amount", "income_frequency"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if the household is below the income limit for their household size
        """
        income_limits = {
            1: 66_300,
            2: 75_750,
            3: 85_200,
            4: 94_560,
            5: 102_250,
            6: 109_800,
            7: 117_400,
            8: 124_950,
        }
        household_income = screen.calc_gross_income("yearly", ["all"])
        income_limit = income_limits[screen.household_size]
        return household_income <= income_limit


class ForeclosureFinAssistProgram(UrgentNeedFunction):
    dependencies = ["household_size", "income_amount", "income_frequency", "county"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if the household is at or below 80% the income limit for their household size & they live in Denver
        """
        income_limits = {
            1: 66_300,
            2: 75_750,
            3: 85_200,
            4: 94_560,
            5: 102_250,
            6: 109_800,
            7: 117_400,
            8: 124_950,
        }
        household_income = screen.calc_gross_income("yearly", ["all"])
        income_limit = income_limits[screen.household_size]
        return household_income <= income_limit and screen.county == "Denver County"


class EocIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"
    range_name = "'2023'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class Eoc(UrgentNeedFunction):
    limits_cache = EocIncomeLimitCache()
    dependencies = ["income_amount", "income_frequency", "household_size", "county"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if the household is below the income limit for their county and household size
        """

        income = int(screen.calc_gross_income("yearly", ["all"]))

        limits = Eoc.limits_cache.fetch()

        if screen.county not in limits:
            return False

        income_limit = limits[screen.county][screen.household_size - 1]

        return income < income_limit


class CoLegalServices(UrgentNeedFunction):
    dependencies = ["income_amount", "income_frequency", "household_size", "age"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if the household is has an income bellow 200% FPL or someone in the household is over 60 years old
        """
        fpl = FederalPoveryLimit.objects.get(year="THIS YEAR").as_dict()
        is_income_eligible = screen.calc_gross_income("yearly", ["all"]) < fpl[screen.household_size]
        is_age_eligible = screen.num_adults(age_max=60) > 0
        return is_income_eligible or is_age_eligible


class CoEmergencyMortgageIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1M_BQxs135UV4uO-CUpHtt9Xy89l1RmSufdP9c3nEh-M"
    range_name = "'100% AMI 2023'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0] + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class CoEmergencyMortgageAssistance(UrgentNeedFunction):
    limits_cache = CoEmergencyMortgageIncomeLimitCache()
    dependencies = ["income_amount", "income_frequency", "household_size", "county"]

    @classmethod
    def eligible(cls, screen: Screen):
        income = int(screen.calc_gross_income("yearly", ["all"]))

        limits = CoEmergencyMortgageAssistance.limits_cache.fetch()

        if screen.county not in limits:
            return False

        income_limit = limits[screen.county][screen.household_size - 1]

        return income < income_limit


class ChildFirst(UrgentNeedFunction):
    dependencies = ["age", "county"]

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if the household has a child aged 0-5 and lives in an eligible county
        """
        is_age_eligible = screen.num_children(age_max=5) > 0
        eligible_counties = [
            "Adams County",
            "Alamosa County",
            "Arapahoe County",
            "Bent County",
            "Boulder County",
            "Broomfield County",
            "Chaffee County",
            "Clear Creek County",
            "Conejos County",
            "Costilla County",
            "Crowley County",
            "Custer County",
            "Douglas County",
            "El Paso County",
            "Fremont County",
            "Gilpin County",
            "Jefferson County",
            "Lake County",
            "Mineral County",
            "Otero County",
            "Rio Grand County",
            "Routt County",
            "Saguache County",
            "Weld County",
        ]

        return is_age_eligible and screen.county in eligible_counties


class EarlyChildhoodMentalHealthSupport(ChildAgeFunction):
    max_age = 5


class ParentsOfPreschoolYoungsters(UrgentNeedFunction):
    dependencies = ["age", "county"]
    counties = [
        "Adams County",
        "Alamosa County",
        "Arapahoe County",
        "Costilla County",
        "Crowley County",
        "Denver County",
        "Dolores County",
        "Jefferson County",
        "Montezuma County",
        "Otero County",
        "Pueblo County",
        "Saguache County",
        "Weld County",
    ]
    min_age = 2
    max_age = 5

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if a child is between 2 and 5 and lives in an eligible county
        """
        age_eligible = screen.num_children(age_min=cls.min_age, age_max=cls.max_age) > 0
        county_eligible = screen.county in cls.counties

        return age_eligible and county_eligible


class ParentsAsTeacher(UrgentNeedFunction):
    dependencies = ["age", "county"]
    counties = [
        "Adams County",
        "Alamosa County",
        "Arapahoe County",
        "Bent County",
        "Boulder County",
        "Conejos County",
        "Costilla County",
        "Crowley County",
        "Delta County",
        "Denver County",
        "Dolores County",
        "El Paso County",
        "Fremont County",
        "Gunnison County",
        "Huerfano County",
        "Jefferson County",
        "La Plata County",
        "Larimer County",
        "Las Animas County",
        "Mesa County",
        "Montezuma County",
        "Montrose County",
        "Morgan County",
        "Otero County",
        "Ouray County",
        "Park County",
        "Pueblo County",
        "Routt County",
        "Saguache County",
        "San Miguel County",
        "Teller County",
    ]
    max_age = 5

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if there is a child younger than 5 and lives in an eligible county
        """
        age_eligible = screen.num_children(age_max=cls.max_age) > 0
        county_eligible = screen.county in cls.counties

        return age_eligible and county_eligible


class DenverEmergencyAssistance(UrgentNeedFunction):
    dependencies = ["county", "income_amount", "income_frequency", "household_size"]
    county = "Denver County"
    fpl_percent = 4

    @classmethod
    def eligible(cls, screen: Screen):
        """
        Return True if the household is bellow 400% fpl and lives in Denver
        """
        county_eligible = screen.county == cls.county
        fpl = FederalPoveryLimit.objects.get(year="THIS YEAR").as_dict()
        income_eligible = screen.calc_gross_income("yearly", ["all"]) < fpl[screen.household_size] * cls.fpl_percent

        return county_eligible and income_eligible


class EarlyIntervention(ChildAgeFunction):
    max_age = 2
