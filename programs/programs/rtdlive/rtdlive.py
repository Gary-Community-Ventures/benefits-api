from decimal import Decimal
from django.conf import settings
import math

def calculate_rtdlive(screen):
    eligibility = eligibility_rtdlive(screen)
    value = value_rtdlive(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_rtdlive(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    denver_metro_zips = [80023,80022,80103,80701,80010,80249,80601,80603,80234,80642,80002,80516,80030,80020,80045,
                         80220,80652,80640,80241,80216,80024,80102,80137,80011,80239,80003,80654,80019,80212,80238,
                         80229,80602,80105,80136,80018,80233,80260,80031,80221,80643,80757,80103,80010,80012,80013,
                         80219,80828,80122,80123,80120,80014,80129,80101,80111,80246,80128,80045,80237,80220,80017,
                         80102,80137,80011,80124,80019,80110,80113,80236,80223,80125,80105,80136,80112,80016,80015,
                         80018,80230,80126,80121,80247,80231,80224,80222,80209,80210,80138,80134,80107,80757,80023,
                         80301,80503,80403,80303,80025,80305,80544,80482,80447,80007,80302,80516,80027,80446,80020,
                         80513,80517,80501,80021,80310,80466,80510,80304,80026,80540,80504,80422,80471,80481,80455,
                         80023,80603,80234,80007,80516,80027,80020,80021,80005,80602,80026,80031,80514,80022,80010,
                         80012,80204,80249,80219,80603,80202,80214,80293,80642,80002,80123,80014,80206,80235,80111,
                         80246,80045,80237,80220,80207,80290,80127,80216,80137,80011,80239,80205,80227,80232,80019,
                         80212,80110,80113,80236,80223,80238,80211,80226,80016,80015,80203,80230,80294,80033,80221,
                         80247,80231,80224,80222,80209,80210,80218,80264,80863,80908,80132,80131,80425,80122,80120,
                         80129,80104,80109,80106,80133,80128,80116,80433,80127,80108,80827,80124,80130,80125,80118,
                         80112,80016,80126,80138,80134,80135,80107,80403,80204,80219,80214,80456,80303,80025,80427,
                         80007,80425,80421,80002,80123,80027,80235,80228,80030,80020,80128,80448,80457,80433,80127,
                         80470,80419,80021,80439,80227,80232,80827,80005,80004,80465,80003,80212,80236,80401,80226,
                         80454,80125,80422,80453,80033,80031,80135,80215]

    frequency = "yearly"
    income_limit = 1.85*settings.FPL[screen.household_size]
    # INCOME TEST -- you can apply for RTD Live with only pay stubs, so we limit to wages here
    income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, income_types)

    if gross_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append("Calculated income of "\
            +str(math.trunc(gross_income))+" for a household with "\
            +str(screen.household_size)\
            +" members is above the income limit of "\
            +str(income_limit))
    else:
        eligibility["passed"].append(
            "Calculated income of "\
            +str(math.trunc(gross_income))\
            +" for a household with "\
            +str(screen.household_size)\
            +" members is below the income limit of "\
            +str(income_limit))

    return eligibility

def value_rtdlive(screen):
    value = 750

    return value