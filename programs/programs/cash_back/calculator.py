

def calculate_chash_back(screen, data):
    eligibility = eligibility_chash_back(screen)
    value = value_chash_back(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_chash_back(screen):

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    adults = screen.num_adults(age_max=18)
    if adults < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "Colorado Cash Back is available to individuals 18+"))
    else:
        eligibility["passed"].append((
            "Colorado Cash Back is available to individuals 18+"))

    return eligibility


def value_chash_back(screen):
    adults = screen.num_adults(age_max=18)
    value = adults * 750
    return value
