

def calculate_cocb(screen, data):
    eligibility = eligibility_cocb(screen)
    value = value_cocb(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_cocb(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    return eligibility


def value_cocb(screen):
    adults = screen.num_adults(age_max=18)
    value = adults * 750
    return value