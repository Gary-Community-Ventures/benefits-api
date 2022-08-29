from django.conf import settings
from django.utils.translation import gettext as _
import math


def calculate_chp(screen, data):
    eligibility = eligibility_chp(screen, data)
    value = value_chp(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_chp(screen, data):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    # Children age 18 and under and pregnant women age 19 and over.
    # Applicants with household income under 260% of the Federal Poverty Level (FPL).
    # Colorado Residents
    # Lawfully residing children and pregnant women with no five year waiting period
    # Applicants not eligible for Health First Colorado
    # Applicants who do not have other health insurance
    child_age_limit = 18
    frequency = "yearly"

    # MEDICAID eligibility test
    for row in data:
        if row['short_name'] == 'medicaid':
            if row['eligible'] == True:
                eligibility["eligible"] = False
                eligibility["failed"].append(_("Individuals who are eligible for Health First Colorado (MEDICAID) are not eligible for CHP+"))

    # Child or Pregnant Test
    eligible_children = screen.num_children(age_max=child_age_limit, include_pregnant=True)
    if eligible_children < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append(_("Children age 18 and under and pregnant women age 19 and over."))

    # INCOME TEST
    income_limit = 2.6*settings.FPL[screen.household_size]
    income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, income_types)

    # income test
    if gross_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append(_("Calculated income of ")\
            +str(math.trunc(gross_income))+_(" for a household with ")\
            +str(screen.household_size)\
            +_(" members is above the income limit of ")\
            +str(income_limit))
    else:
        eligibility["passed"].append(
            _("Calculated income of ")\
            +str(math.trunc(gross_income))\
            +_(" for a household with ")\
            +str(screen.household_size)\
            +_(" members is below the income limit of ")\
            +str(income_limit))

    return eligibility

def value_chp(screen):
    child_age_limit = 18
    eligible_children = screen.num_children(age_max=child_age_limit, include_pregnant=True)
    value = 200 * 12 * eligible_children

    return value