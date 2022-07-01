from decimal import Decimal

def eligibility_acp(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    # Variables that may change over time
    # household size : income limit
    income_bands = {
        1: 27180,
        2: 36620,
        3: 46060,
        4: 55500,
        5: 64940,
        6: 74380,
        7: 83820,
        8: 93260
    }
    frequency = "yearly"

    income_limit = income_bands[screen.household_size]

    # INCOME TEST -- you can apply to ACP with only pay stubs, so we limit to wages here
    income_types = ["wages", "selfEmployment"]
    acp_income = screen.calc_gross_income(frequency, income_types)

    if acp_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append("Calculated income of "\
            +str(acp_income)+" for a household with "\
            +str(screen.household_size)\
            +" members is above the income limit of "\
            +str(income_limit))
    else:
        eligibility["passed"].append(
            "Calculated income of "\
            +str(acp_income)\
            +" for a household with "\
            +str(screen.household_size)\
            +" members is below the income limit of "\
            +str(income_limit))

    return eligibility

def value_acp(screen):
    value = 35

    return value