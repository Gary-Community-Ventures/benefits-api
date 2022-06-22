

def eligibility_snap(screen):
    eligible = True

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

    if screen.total_income() > income_limit:
        eligible = False

    return eligible

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