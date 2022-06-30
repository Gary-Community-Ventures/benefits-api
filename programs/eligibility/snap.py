from decimal import Decimal

def eligibility_snap(screen):
    eligible = True
    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    income_bands = {
        1: 2148,
        2: 2904,
        3: 3660,
        4: 4418,
        5: 5174,
        6: 5930,
        7: 6688,
        8: 7444
    }

    income_limit = income_bands[screen.household_size]
    frequency = "monthly"

    # INCOME TEST -- SNAP only counts 80% of earned income against eligibility
    earned_income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, ["all"])
    earned_gross_income = screen.calc_gross_income(frequency, earned_income_types)
    unearned_gross_income = gross_income - earned_gross_income
    snap_gross_income = Decimal(.8) * earned_gross_income + unearned_gross_income
    expense_types = ["childSupport", "dependentCare", "childCare", "rent", "heating", "cooling", "mortgage", "utilities", "telephone"]

    # SNAP allows disabled or applicants over the age of 60 to deduct medical
    if screen.disabled or screen.applicant_age >= 60:
        expense_types.append("medical")
    snap_expenses = screen.calc_expenses(frequency, expense_types)
    net_income = snap_gross_income - snap_expenses

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
    if screen.applicant_age >= 60 and screen.household_assets >= 3750:
        eligibility["eligible"] = False
        eligibility["failed"].append("Households with members at or above the age of 60 have to pass an asset test."\
                " Your reported household assets of "\
                +str(screen.household_assets)\
                +" is above the limit of 3750")
    elif screen.applicant_age >= 60:
        eligibility["passed"].append("Households with members at or above the age of 60 have to pass an asset test."\
                " Your reported household assets of "\
                +str(screen.household_assets)\
                +" is below the limit of 3750")
    else:
        eligibility["passed"].append("Households with members at or above the age of 60 have to pass an asset test."\
                +" You did not report any household members at or above this age.")

    # ABAWD TEST -- post pandemic we will need to add test for able bodied workers

    return eligibility

def value_snap(screen):
    value = 0

    value_bands = {
        1: 250,
        2: 459,
        3: 658,
        4: 835,
        5: 992,
        6: 1190,
        7: 1316,
        8: 1504
    }

    value = value_bands[screen.household_size]

    return value