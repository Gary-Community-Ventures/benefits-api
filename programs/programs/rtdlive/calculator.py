from programs.co_county_zips import counties_from_zip
import programs.programs.messages as messages


def calculate_rtdlive(screen, data, program):
    eligibility = eligibility_rtdlive(screen, program)
    value = value_rtdlive(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_rtdlive(screen, program):

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    eligible_counties = ['Adams County', 'Arapahoe County', 'Boulder County',
                         'Broomfield County', 'Denver County',
                         'Douglas County', 'Jefferson County']
    frequency = "yearly"

    # INCOME TEST
    fpl = program.fpl.as_dict()
    income_limit = 1.85 * fpl[screen.household_size]
    income_types = ['all']
    gross_income = screen.calc_gross_income(frequency, income_types)

    # adults in household test
    qualifying_adults = 0
    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age >= 20 and household_member.age <= 64:
            qualifying_adults += 1

    # geography test
    county_eligible = False
    if not screen.county:
        counties = counties_from_zip(screen.zipcode)
    else:
        counties = [screen.county]

    for county in counties:
        if county in eligible_counties:
            county_eligible = True

    if qualifying_adults < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.adult(20, 64))
    else:
        eligibility["passed"].append(messages.adult(20, 64))

    if not county_eligible:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.location())
    else:
        eligibility["passed"].append(messages.location())

    # income test
    if gross_income > income_limit:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.income(gross_income, income_limit))
    else:
        eligibility["passed"].append(messages.income(gross_income, income_limit))

    return eligibility


def value_rtdlive(screen):
    qualifying_adults = 0
    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age >= 20 and household_member.age <= 64:
            qualifying_adults += 1

    value = 750 * qualifying_adults

    return value
