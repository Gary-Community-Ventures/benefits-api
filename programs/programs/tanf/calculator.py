from decimal import Decimal
import programs.programs.messages as messages


def calculate_tanf(screen, data):
    value = 0
    child_age_limit = 19
    children = screen.num_children(age_max=child_age_limit,
                                   include_pregnant=True,
                                   child_relationship=['child'])

    guardians = screen.num_guardians()

    eligibility = eligibility_tanf(screen, children, guardians)

    if eligibility['eligible']:
        value = value_tanf(screen, children, guardians)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_tanf(screen, children, guardians):
    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }
    frequency = "monthly"
    eligibility_income_types = ["wages", "selfEmployment", "unemployment",
                                "cashAssistance", "disabilityMedicaid",
                                "sSI", "sSDependent", "sSDisability",
                                "sSSurvivor", "sSRetirement", "cOSDisability",
                                "veteran", "pension", "deferredComp",
                                "workersComp", "alimony", "boarder", "gifts",
                                "rental", "investment", "childSupport"]

    one_parent_income_bands = {
        1: 331,
        2: 421,
        3: 510,
        4: 605,
        5: 697,
        6: 770,
        7: 844,
        8: 920,
        9: 992,
        10: 1065
    }

    two_parent_income_bands = {
        1: 439,
        2: 533,
        3: 628,
        4: 716,
        5: 787,
        6: 861,
        7: 937,
        8: 1009,
        9: 1082,
        10: 1155
    }

    child_only_income_bands = {
        1: 117,
        2: 245,
        3: 368,
        4: 490,
        5: 587,
        6: 678,
        7: 755,
        8: 830,
        9: 904,
        10: 977
    }

    # CHILD TEST
    if children < 1:
        eligibility["failed"].append(messages.child())
        eligibility["eligible"] = False
        return eligibility
    else:
        eligibility["passed"].append(messages.child())

    # SET INCOME LIMIT DEPENDING ON HOUSEHOLD COMPOSITION
    if guardians == 0:
        income_bands = child_only_income_bands
    elif guardians == 1:
        income_bands = one_parent_income_bands
    elif guardians >= 2:
        income_bands = two_parent_income_bands

    income_limit = income_bands[children]
    earned_income = screen.calc_gross_income(frequency,
                                             eligibility_income_types)
    tanf_earned_income = earned_income - 90
    if tanf_earned_income < 0:
        tanf_earned_income = 0

    # INCOME TEST
    income_test_description = (messages.income(tanf_earned_income, income_limit))

    if tanf_earned_income <= income_limit:
        eligibility['passed'].append(income_test_description)
    else:
        eligibility['eligible'] = False
        eligibility['failed'].append(income_test_description)

    return eligibility


def value_tanf(screen, children, guardians):
    frequency = "monthly"
    unearned_income_types = ["unemployment", "cashAssistance",
                             "disabilityMedicaid", "sSI", "sSDependent",
                             "sSDisability", "sSSurvivor", "sSRetirement",
                             "cOSDisability", "veteran", "pension",
                             "deferredComp", "workersComp", "alimony",
                             "boarder", "gifts", "rental", "investment"]
    earned_income_types = ["wages", "selfEmployment"]

    child_only_value_bands = {
        1: 156,
        2: 326,
        3: 489,
        4: 653,
        5: 783,
        6: 904,
        7: 1007,
        8: 1105,
        9: 1205,
        10: 1315,
    }

    one_parent_value_bands = {
        1: 440,
        2: 559,
        3: 679,
        4: 806,
        5: 929,
        6: 1026,
        7: 1125,
        8: 1225,
        9: 1322,
        10: 1418,
    }

    two_parent_value_bands = {
        1: 585,
        2: 710,
        3: 836,
        4: 953,
        5: 1048,
        6: 1147,
        7: 1249,
        8: 1345,
        9: 1440,
        10: 1538,
    }

    if guardians < 1:
        value_band = child_only_value_bands
    elif guardians == 1:
        value_band = one_parent_value_bands
    elif guardians >= 2:
        value_band = two_parent_value_bands

    earned_income = screen.calc_gross_income(frequency, earned_income_types)
    tanf_earned_income = Decimal(.33) * earned_income
    unearned_income = screen.calc_gross_income(frequency,
                                               unearned_income_types)
    monthly_value = value_band[children] - tanf_earned_income - unearned_income
    value = int(monthly_value * 12)
    return value
