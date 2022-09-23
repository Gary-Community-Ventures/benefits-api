from django.utils.translation import gettext as _
from programs.sheets import sheets_get_data
from programs.co_county_zips import counties_from_zip

import re
import math


def calculate_cccap(screen, data):
    eligibility = eligibility_cccap(screen)
    value = value_cccap(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_cccap(screen):
    eligible = True

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    #Family must have at least one child under 13 years old (19 years old if special needs or disability).
    #county level income requirements
    #are working, seeking employment, or participating in training/education

    # CHILD TEST
    # todo: support children with special needs
    cccap_children = num_cccap_children(screen)

    if cccap_children < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "To qualify for CCCAP a family must have at least one child under 13 ",
            "years old (19 years old if special needs or disability)."))
    else:
        eligibility["passed"].append((
            "To qualify for CCCAP a family must have at least one child under 13 ",
            "years old (19 years old if special needs or disability)."))

    # WORKING TEST
    # todo: support families seeking work

    # INCOME TEST
    counties = counties_from_zip(screen.zipcode)
    county_name = counties[0]
    frequency = "yearly"
    cccap_county_data = cccap_county_values(county_name)
    if not cccap_county_data:
        eligibility["eligible"] = False
        eligibility["failed"].append((
            "To qualify for CCCAP a family must reside in Colorado. ",
            county_name,
            " was not found in the list of known counties."))
        return eligibility

    income_types = ['all']
    gross_income = screen.calc_gross_income(frequency, income_types)
    if cccap_children >= 1:
        income_limit = cccap_county_data[screen.household_size] * 12
        if gross_income > income_limit:
            eligibility["eligible"] = False
            eligibility["failed"].append((
                "Calculated income of ",
                str(math.trunc(gross_income)),
                " for a household with ",
                str(screen.household_size),
                " members is above the income limit of ",
                str(income_limit),
                " for ",
                county_name))
        else:
            eligibility["passed"].append((
                "Calculated income of ",
                str(math.trunc(gross_income)),
                " for a household with ",
                str(screen.household_size),
                " members is below the income limit of ",
                str(income_limit),
                " for ",
                county_name))

    return eligibility


def value_cccap(screen):
    value = 0
    preschool_value = 6000
    afterschool_value = 1700

    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age <= 4:
            value += preschool_value
        elif household_member.age < 13:
            value += afterschool_value
        elif household_member.age >= 13 and \
                household_member.age <= 19 and \
                household_member.disabled:
            value += afterschool_value

    return value


def cccap_county_values(county_name):
    match = False
    spreadsheet_id = '1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk'
    range_name = 'Sheet1!A14:J78'
    sheet_values = sheets_get_data(spreadsheet_id, range_name)
    if not sheet_values:
        return match

    cccap_county_name = county_name.replace(" County", "")
    non_decimal = re.compile(r'[^\d.]+')

    for row in sheet_values:
        if row[0] == cccap_county_name:
            match = {
                2: float(non_decimal.sub('', row[2])),
                3: float(non_decimal.sub('', row[3])),
                4: float(non_decimal.sub('', row[4])),
                5: float(non_decimal.sub('', row[5])),
                6: float(non_decimal.sub('', row[6])),
                7: float(non_decimal.sub('', row[7])),
                8: float(non_decimal.sub('', row[8])),
                9: float(non_decimal.sub('', row[9]))
            }

    return match


def num_cccap_children(screen):
    children = 0
    child_relationship = ['child', 'fosterChild']

    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age <= 12:
            children += 1
        elif household_member.age >= 13 and \
                household_member.age <= 19 and \
                household_member.disabled:
            children += 1

    return children