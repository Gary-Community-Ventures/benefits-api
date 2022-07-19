from decimal import Decimal

def eligibility_tanf(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    # Variables that may change over time
    # household size : income limit

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

    frequency = "monthly"
    child_age_limit = 19
    has_child = False
    adults =

    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age <= 19:
            has_child = True
        if

    income_limit = income_bands[screen.household_size]

    # INCOME TEST -- SNAP only counts 80% of earned income against eligibility
    earned_income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, ["all"])
    earned_gross_income = screen.calc_gross_income(frequency, earned_income_types)
    unearned_gross_income = gross_income - earned_gross_income
    tanf_gross_income = Decimal(.8) * earned_gross_income + unearned_gross_income
    expense_types = ["childSupport", "dependentCare", "childCare", "rent", "heating", "cooling", "mortgage", "utilities", "telephone"]

    # SNAP allows disabled or applicants over the age of 60 to deduct medical
    if screen.disabled or screen.applicant_age >= older_adult:
        expense_types.append("medical")
    tanf_expenses = screen.calc_expenses(frequency, expense_types)
    net_income = tanf_gross_income - tanf_expenses

    if net_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append("Calculated net income of "\
            +str(net_income)+" for a household with "\
            +str(screen.household_size)\
            +" members is above the income limit of "\
            +str(income_limit))
    else:
        eligibility["passed"].append(
            "Calculated net income of "\
            +str(net_income)\
            +" for a household with "\
            +str(screen.household_size)\
            +" members is below the income limit of "\
            +str(income_limit))

    # ASSET TEST -- SNAP requires an asset test for applicants over the age of 60
    if screen.applicant_age >= older_adult and screen.household_assets >= older_adult_asset_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append("Households with members at or above the age of 60 have to pass an asset test."\
                " Your reported household assets of "\
                +str(screen.household_assets)\
                +" is above the limit of 3750")
    elif screen.applicant_age >= older_adult:
        eligibility["passed"].append("Households with members at or above the age of 60 have to pass an asset test."\
                " Your reported household assets of "\
                +str(screen.household_assets)\
                +" is below the limit of 3750")
    else:
        eligibility["passed"].append("Households with members at or above the age of 60 have to pass an asset test."\
                +" You did not report any household members at or above this age.")

    # ABAWD TEST -- post pandemic we will need to add test for able bodied workers

    return eligibility

def value_tanf(screen):
    value = 0

    # Variables that may change over time
    # household size : maximum monthly allotment
    value_bands = {
        1: 250*12,
        2: 459*12,
        3: 658*12,
        4: 835*12,
        5: 992*12,
        6: 1190*12,
        7: 1316*12,
        8: 1504*12
    }

    value = value_bands[screen.household_size]

    return value