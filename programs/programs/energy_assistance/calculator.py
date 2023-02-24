import programs.programs.messages as messages


def calculate_energy_assistance(screen, data):
    eligibility = eligibility_energy_assistance(screen)
    value = value_energy_assistance(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_energy_assistance(screen):

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
        eligibility["failed"].append(messages.income(leap_income, income_limit))
    else:
        eligibility["passed"].append(messages.income(leap_income, income_limit))

    return eligibility


def value_energy_assistance(screen):
    value = 362

    return value
