from screener.models import Screen
from programs.models import FederalPoveryLimit
from programs.util import Dependencies
from integrations.services.sheets import GoogleSheetsCache


class UrgentNeedFunction:
    """
    Base class for all urgent need conditions
    """

    dependencies = []

    def __init__(self, screen: Screen, missing_dependencies: Dependencies, data) -> None:
        self.screen = screen
        self.missing_dependencies = missing_dependencies
        self.data = data

    def calc(self):
        """
        Calculate if the urgent need can be calculated and if the condition is met
        """
        if not self.can_calc():
            return False

        return self.eligible()

    def eligible(self):
        """
        Returns if the condition is met
        """
        return True

    def can_calc(self):
        """
        Returns if the condition can be calculated
        """
        if self.missing_dependencies.has(*self.dependencies):
            return False

        return True


class ChildAgeFunction(UrgentNeedFunction):
    dependencies = ["age"]
    min_age = 0
    max_age = 18

    def eligible(self):
        """
        return True if the child is between the ages of min_age and max_age
        """
        return self.screen.num_children(age_min=self.min_age, age_max=self.max_age) > 0


class LivesInDenver(UrgentNeedFunction):
    dependencies = ["county"]
    county = "Denver County"

    def eligible(self):
        """
        Household lives in the Denver County
        """
        return self.screen.county == self.county


class MealInCounties(UrgentNeedFunction):
    dependencies = ["county"]
    counties = ["Denver County", "Jefferson County"]

    def eligible(self):
        """
        Household lives in Denver or Jefferson County
        """
        return self.screen.county in self.counties


class HelpkitchenZipcode(UrgentNeedFunction):
    dependencies = ["zipcode"]
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

    def eligible(self):
        """
        Lives in a zipcode that is eligible for HelpKitchen
        """
        return self.screen.zipcode in self.zipcodes


class Child(ChildAgeFunction):
    pass


class BiaFoodDelivery(UrgentNeedFunction):
    dependencies = ["county"]
    eligible_counties = [
        "Adams County",
        "Arapahoe County",
        "Denver County",
        "Jefferson County",
    ]

    def eligible(self):
        """
        Return True if in Adams, Arapahoe, Denver or Jefferson county
        """
        return self.screen.county in self.eligible_counties


class Trua(UrgentNeedFunction):
    dependencies = ["household_size", "income_amount", "income_frequency"]
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

    def eligible(self):
        """
        Return True if the household is below the income limit for their household size
        """
        household_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = self.income_limits[self.screen.household_size]
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])

        return household_income <= income_limit and has_rent_or_mortgage


class ForeclosureFinAssistProgram(UrgentNeedFunction):
    dependencies = ["household_size", "income_amount", "income_frequency", "county"]
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

    def eligible(self):
        """
        Return True if the household is at or below 80% the income limit for their household size & they live in Denver
        """
        household_income = self.screen.calc_gross_income("yearly", ["all"])
        income_limit = self.income_limits[self.screen.household_size]
        has_mortgage = self.screen.has_expense(["mortgage"])
        return household_income <= income_limit and self.screen.county == "Denver County" and has_mortgage


class EocIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"
    range_name = "'current'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class Eoc(UrgentNeedFunction):
    dependencies = ["income_amount", "income_frequency", "household_size", "county"]
    limits_cache = EocIncomeLimitCache()

    def eligible(self):
        """
        Return True if the household is below the income limit for their county and household size
        """

        income = int(self.screen.calc_gross_income("yearly", ["all"]))

        limits = Eoc.limits_cache.fetch()

        if self.screen.county not in limits:
            return False

        income_limit = limits[self.screen.county][self.screen.household_size - 1]

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])

        return income < income_limit and has_rent_or_mortgage


class CoLegalServices(UrgentNeedFunction):
    dependencies = ["income_amount", "income_frequency", "household_size", "age"]
    max_age = 60

    def eligible(self):
        """
        Return True if the household is has an income bellow 200% FPL or someone in the household is over 60 years old
        """
        fpl = FederalPoveryLimit.objects.get(year="THIS YEAR").as_dict()
        is_income_eligible = self.screen.calc_gross_income("yearly", ["all"]) < fpl[self.screen.household_size]
        is_age_eligible = self.screen.num_adults(age_max=self.max_age) > 0
        main_eligibility = is_age_eligible or is_income_eligible
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        # don't apply the rent/mortgage condition to legal services need
        rent_mortgage_eligible = has_rent_or_mortgage or self.screen.needs_legal_services

        return main_eligibility and rent_mortgage_eligible


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

    def eligible(self):
        income = int(self.screen.calc_gross_income("yearly", ["all"]))

        limits = CoEmergencyMortgageAssistance.limits_cache.fetch()

        if self.screen.county not in limits:
            return False

        income_limit = limits[self.screen.county][self.screen.household_size - 1]
        has_mortgage = self.screen.has_expense(["mortgage"])

        return income < income_limit and has_mortgage


class ChildFirst(UrgentNeedFunction):
    dependencies = ["age", "county"]
    max_age = 5
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

    def eligible(self):
        """
        Return True if the household has a child aged 0-5 and lives in an eligible county
        """
        is_age_eligible = self.screen.num_children(age_max=self.max_age) > 0

        return is_age_eligible and self.screen.county in self.eligible_counties


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

    def eligible(self):
        """
        Return True if a child is between 2 and 5 and lives in an eligible county
        """
        age_eligible = self.screen.num_children(age_min=self.min_age, age_max=self.max_age) > 0
        county_eligible = self.screen.county in self.counties

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

    def eligible(self):
        """
        Return True if there is a child younger than 5 and lives in an eligible county
        """
        age_eligible = self.screen.num_children(age_max=self.max_age) > 0
        county_eligible = self.screen.county in self.counties

        return age_eligible and county_eligible


class SnapEmployment(UrgentNeedFunction):
    dependencies = ["county"]
    county = "Denver County"

    def eligible(self):
        """
        Return True if the household is SNAP eligible and lives in Denver
        """
        county_eligible = self.screen.county == self.county

        snap_eligible = self.screen.has_benefit("snap")
        for program in self.data:
            if program["name_abbreviated"] != "snap":
                continue

            if program["eligible"]:
                snap_eligible = True
            break

        return county_eligible and snap_eligible


class DenverEmergencyAssistance(UrgentNeedFunction):
    dependencies = ["county", "income_amount", "income_frequency", "household_size"]
    county = "Denver County"
    fpl_percent = 4

    def eligible(self):
        """
        Return True if the household is bellow 400% fpl and lives in Denver
        """
        county_eligible = self.screen.county == self.county
        fpl = FederalPoveryLimit.objects.get(year="THIS YEAR").as_dict()
        income_eligible = (
            self.screen.calc_gross_income("yearly", ["all"]) < fpl[self.screen.household_size] * self.fpl_percent
        )
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])

        return county_eligible and income_eligible and has_rent_or_mortgage


class EarlyIntervention(ChildAgeFunction):
    max_age = 2


class HasRentOrMortgage(UrgentNeedFunction):
    def eligible(self):
        """
        Return True if rent or mortgage is listed as an expense
        """
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])

        return has_rent_or_mortgage


DIAPER_BANK_COUNTIES = [
    "Adams County",
    "Arapahoe County",
    "Boulder County",
    "Broomfield County",
    "Denver County",
    "Douglas County",
    "Jefferson County",
    "Larimer County",
    "Mesa County",
    "Weld County",
]


class FamilyResourceCenterAssociation(UrgentNeedFunction):
    ineligible_counties = DIAPER_BANK_COUNTIES

    def eligible(self):
        """
        Return True for users who live in an eligible county
        """

        return self.screen.county not in self.ineligible_counties


class NationalDiaperBank(UrgentNeedFunction):
    eligible_counties = DIAPER_BANK_COUNTIES

    def eligible(self):
        """
        Return True for users who live in an eligible county
        """

        return self.screen.county in self.eligible_counties


urgent_need_functions: dict[str, type[UrgentNeedFunction]] = {
    "denver": LivesInDenver,
    "meal": MealInCounties,
    "helpkitchen_zipcode": HelpkitchenZipcode,
    "child": Child,
    "bia_food_delivery": BiaFoodDelivery,
    "trua": Trua,
    "ffap": ForeclosureFinAssistProgram,
    "eoc": Eoc,
    "co_legal_services": CoLegalServices,
    "co_emergency_mortgage": CoEmergencyMortgageAssistance,
    "child_first": ChildFirst,
    "ecmh": EarlyChildhoodMentalHealthSupport,
    "hippy": ParentsOfPreschoolYoungsters,
    "pat": ParentsAsTeacher,
    "snap_employment": SnapEmployment,
    "eic": EarlyIntervention,
    "deap": DenverEmergencyAssistance,
    "has_rent_or_mtg": HasRentOrMortgage,
    "frca": FamilyResourceCenterAssociation,
    "diaper_bank": NationalDiaperBank,
}
