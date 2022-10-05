from decimal import Decimal
from programs.co_county_zips import counties_from_zip
from django.conf import settings
from django.utils.translation import gettext as _
import math
import json


def calculate_rtdlive(screen, data):
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

    # INCOME TEST
    income_limit = 1.85*settings.FPL[screen.household_size]
    income_types = ['all']
    gross_income = screen.calc_gross_income(frequency, income_types)

    # adults in household test
    qualifying_adults = 0
    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age >= 20 and household_member.age <= 64:
            qualifying_adults += 1

    # geography test
    county_eligible = False
    if not screen.county:
        counties = counties_from_zip(screen.zipcode)
        display_location = screen.zipcode
    else:
        counties = [screen.county]
        display_location = screen.county

    for county in counties:
        if county in eligible_counties:
            county_eligible = True

    if qualifying_adults < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "RTD Live is available to adults ages 20-64."))
    else:
        eligibility["passed"].append((
            "RTD Live is available to adults ages 20-64."))

    if not county_eligible:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "To qualify for RTD live you must live in the RTD service area."))
    else:
        eligibility["passed"].append((
            display_location,
            " is within the RTD service area."))

    # income test
    if gross_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "Calculated income of ",
            str(math.trunc(gross_income)),
            " for a household with ",
            str(screen.household_size),
            " members is above the income limit of ",
            str(income_limit)))
    else:
        eligibility["passed"].append((
            "Calculated income of ",
            str(math.trunc(gross_income)),
            " for a household with ",
            str(screen.household_size),
            " members is below the income limit of ",
            str(income_limit)))

    return eligibility

def value_rtdlive(screen):
    qualifying_adults = 0
    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age >= 20 and household_member.age <= 64:
            qualifying_adults += 1

    value = 750 * qualifying_adults

    return value