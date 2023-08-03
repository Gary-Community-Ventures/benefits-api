import programs.programs.messages as messages


def calculate_chp(screen, data, program):
    eligibility = eligibility_chp(screen, data, program)
    value = value_chp(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_chp(screen, data, program):

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    # Children age 18 and under and pregnant women age 19 and over.
    # Applicants with household income under 260% of the Federal
    # Poverty Level (FPL).
    # Colorado Residents
    # Lawfully residing children and pregnant women with no five year
    # waiting period
    # Applicants not eligible for Health First Colorado
    # Applicants who do not have other health insurance
    child_age_limit = 18
    frequency = "yearly"

    # MEDICAID eligibility test
    for row in data:
        if row['name_abbreviated'] == 'medicaid':
            if row['eligible'] is True:
                eligibility["eligible"] = False
                eligibility["failed"].append(messages.must_not_have_benefit('Medicaid'))

    # Child or Pregnant Test
    eligible_children = screen.num_children(age_max=child_age_limit,
                                            include_pregnant=True)
    if eligible_children < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.child())

    # INCOME TEST
    fpl = program.fpl.as_dict()
    income_limit = 2.6 * fpl[screen.household_size]
    income_types = ["wages", "selfEmployment"]
    gross_income = screen.calc_gross_income(frequency, income_types)

    # income test
    if gross_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.income(gross_income, income_limit))
    else:
        eligibility["passed"].append(messages.income(gross_income, income_limit))

    return eligibility


def value_chp(screen):
    child_age_limit = 18
    eligible_children = screen.num_children(age_max=child_age_limit,
                                            include_pregnant=True)
    value = 200 * 12 * eligible_children

    return value
