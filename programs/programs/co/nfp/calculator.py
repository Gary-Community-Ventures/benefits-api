from django.utils.translation import gettext as _
import math


def calculate_nfp(screen, data, program):
    eligibility = eligibility_nfp(screen, program)
    value = value_nfp(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_nfp(screen, program):

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    frequency = "yearly"

    # INCOME TEST -- you can apply for RTD Live with only pay stubs,
    # so we limit to wages here
    fpl = program.fpl.as_dict()
    income_limit = 2 * fpl[screen.household_size]
    income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, income_types)

    # income test
    if gross_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append(
            _("Calculated income of ")
            + str(math.trunc(gross_income)) + _(" for a household with ")
            + str(screen.household_size)
            + _(" members is above the income limit of ")
            + str(income_limit))
    else:
        eligibility["passed"].append(
            _("Calculated income of ")
            + str(math.trunc(gross_income))
            + _(" for a household with ")
            + str(screen.household_size)
            + _(" members is below the income limit of ")
            + str(income_limit))

    return eligibility


def value_nfp(screen):
    value = 750

    return value
