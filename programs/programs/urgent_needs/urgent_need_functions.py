from screener.models import Screen
from programs.models import FederalPoveryLimit
from programs.util import Dependencies
from integrations.util.cache import Cache
from programs.sheets import sheets_get_data


class UrgentNeedFunction:
    '''
    Base class for all urgent need conditions
    '''

    dependencies = []

    @classmethod
    def calc(cls, screen: Screen, missing_dependencies: Dependencies):
        '''
        Calculate if the urgent need can be calculated and if the condition is met
        '''
        if not cls.can_calc(missing_dependencies):
            return False

        return cls.eligible(screen)

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Returns if the condition is met
        '''
        return True

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        '''
        Returns if the condition can be calculated
        '''
        if missing_dependencies.has(*cls.dependencies):
            return False

        return True


class LivesInDenver(UrgentNeedFunction):
    dependencies = ['county']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Household lives in the Denver County
        '''
        return screen.county == 'Denver County'


class MealInCounties(UrgentNeedFunction):
    dependencies = ['county']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Household lives in Denver or Jefferson County
        '''
        eligible_counties = ['Denver County', 'Jefferson County']
        return screen.county in eligible_counties


class HelpkitchenZipcode(UrgentNeedFunction):
    dependencies = ['zipcode']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Lives in a zipcode that is eligible for HelpKitchen
        '''
        zipcodes = [
            '80010',
            '80011',
            '80012',
            '80013',
            '80014',
            '80015',
            '80016',
            '80017',
            '80018',
            '80019',
            '80045',
            '80102',
            '80112',
            '80137',
            '80138',
            '80230',
            '80231',
            '80238',
            '80247',
            '80249',
        ]
        return screen.zipcode in zipcodes


class Child(UrgentNeedFunction):
    dependencies = ['age']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Return True if someone is younger than 18
        '''
        return screen.num_children(child_relationship=['all']) >= 1


class BiaFoodDelivery(UrgentNeedFunction):
    dependencies = ['county']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Return True if in Adams, Arapahoe, Denver or Jefferson county
        '''
        eligible_counties = [
            'Adams County',
            'Arapahoe County',
            'Denver County',
            'Jefferson County',
        ]
        return screen.county in eligible_counties


class Trua(UrgentNeedFunction):
    dependencies = ['household_size', 'income_amount', 'income_frequency']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Return True if the household is below the income limit for their household size
        '''
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
        household_income = screen.calc_gross_income('yearly', ['all'])
        income_limit = income_limits[screen.household_size]
        return household_income <= income_limit


class EocIncomeLimitCache(Cache):
    expire_time = 60 * 60 * 24
    default = {}

    def update(self):
        spreadsheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"
        range_name = "'2023'!A2:I65"
        sheet_values = sheets_get_data(spreadsheet_id, range_name)

        if not sheet_values:
            raise Exception('Sheet unavailable')

        data = {d[0].strip() + ' County': [int(v.replace(',', '')) for v in d[1:]] for d in sheet_values}

        return data


class Eoc(UrgentNeedFunction):
    limits_cache = EocIncomeLimitCache()
    dependencies = ['income_amount', 'income_frequency', 'household_size', 'county']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Return True if the household is below the income limit for their county and household size
        '''

        income = int(screen.calc_gross_income('yearly', ['all']))

        limits = Eoc.limits_cache.fetch()

        if screen.county not in limits:
            return False

        income_limit = limits[screen.county][
            screen.household_size - 1
        ]

        return income < income_limit


class CoLegalServices(UrgentNeedFunction):
    dependencies = ['income_amount', 'income_frequency', 'household_size', 'age']

    @classmethod
    def eligible(cls, screen: Screen):
        '''
        Return True if the household is has an income bellow 200% FPL or someone in the household is over 60 years old
        '''
        fpl = FederalPoveryLimit.objects.get(year='THIS YEAR').as_dict()
        is_income_eligible = (
            screen.calc_gross_income('yearly', ['all']) < fpl[screen.household_size]
        )
        is_age_eligible = screen.num_adults(age_max=60)
        return is_income_eligible or is_age_eligible


class CoEmergencyMortgageIncomeLimitCache(Cache):
    expire_time = 60 * 60 * 24
    default = {}

    def update(self):
        spreadsheet_id = '1M_BQxs135UV4uO-CUpHtt9Xy89l1RmSufdP9c3nEh-M'
        range_name = "'100% AMI 2023'!A2:I65"
        sheet_values = sheets_get_data(spreadsheet_id, range_name)

        if not sheet_values:
            raise Exception('Sheet unavailable')

        data = {d[0] + ' County': [int(v.replace(',', '')) for v in d[1:]] for d in sheet_values}

        return data


class CoEmergencyMortgageAssistance(UrgentNeedFunction):
    limits_cache = CoEmergencyMortgageIncomeLimitCache()
    dependencies = ['income_amount', 'income_frequency', 'household_size', 'county']

    @classmethod
    def eligible(cls, screen: Screen):
        income = int(screen.calc_gross_income('yearly', ['all']))

        limits = CoEmergencyMortgageAssistance.limits_cache.fetch()

        if screen.county not in limits:
            return False

        income_limit = limits[screen.county][
            screen.household_size - 1
        ]

        return income < income_limit
