from decimal import Decimal
from django.utils.translation import gettext as _
import math

def calculate_leap(screen, data):
    eligibility = eligibility_leap(screen)
    value = value_leap(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation

def eligibility_leap(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    # Variables that may change over time
    # household size : income limit
    income_bands = {
        1: 2880,
        2: 3766,
        3: 4652,
        4: 5539,
        5: 6425,
        6: 7311,
        7: 7477,
        8: 7644
    }
    frequency = "monthly"

    income_limit = income_bands[screen.household_size]

    # INCOME TEST
    income_types = ['all']
    leap_income = screen.calc_gross_income(frequency, income_types)

    if leap_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "Calculated income of ",
            str(math.trunc(leap_income)),
            " for a household with ",
            str(screen.household_size),
            " members is above the income limit of ",
            str(income_limit)))
    else:
        eligibility["passed"].append((
            "Calculated income of ",
            str(math.trunc(leap_income)),
            " for a household with ",
            str(screen.household_size),
            " members is below the income limit of ",
            str(income_limit)))

    return eligibility

def value_leap(screen):
    value = 362

    return value