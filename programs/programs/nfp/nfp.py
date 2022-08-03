from decimal import Decimal
from programs.co_county_zips import counties_from_zip
from django.conf import settings
import math
import json


def calculate_nfp(screen, data):
    eligibility = eligibility_nfp(screen)
    value = value_nfp(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_nfp(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    frequency = "yearly"

    # INCOME TEST -- you can apply for RTD Live with only pay stubs, so we limit to wages here
    income_limit = 2*settings.FPL[screen.household_size]
    income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, income_types)

    # income test
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

def value_nfp(screen):
    value = 750

    return value