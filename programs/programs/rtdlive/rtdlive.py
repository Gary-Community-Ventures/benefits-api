from decimal import Decimal
from programs.co_county_zips import counties_from_zip
from django.conf import settings
import math
import json


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

    eligible_counties = ['Adams County', 'Arapahoe County', 'Boulder County', 'Broomfield County', 'Denver County',
                         'Douglas County', 'Jefferson County']
    frequency = "yearly"

    # INCOME TEST -- you can apply for RTD Live with only pay stubs, so we limit to wages here
    income_limit = 1.85*settings.FPL[screen.household_size]
    income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, income_types)

    # geography test
    county_eligible = False
    counties = counties_from_zip(screen.zipcode)
    for county in counties:
        if county in eligible_counties:
            county_eligible = True

    if not county_eligible:
        eligibility["eligible"] = False
        eligibility["failed"].append("To qualify for RTD live you must live in the RTD service area.")
    else:
        eligibility["passed"].append("The zipcode "\
                +screen.zipcode\
                +" is within the RTD service area.")

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

def value_rtdlive(screen):
    value = 750

    return value