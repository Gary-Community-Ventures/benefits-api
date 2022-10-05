

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

    adults = screen.num_adults(age_max=18)
    if adults < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "Colorado Cash Back is available to individuals 18+"))
    else:
        eligibility["passed"].append((
            "Colorado Cash Back is available to individuals 18+"))

    return eligibility


def value_cocb(screen):
    adults = screen.num_adults(age_max=18)
    value = adults * 750
    return value