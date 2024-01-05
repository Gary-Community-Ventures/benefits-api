from programs.sheets import sheets_get_data
from programs.co_county_zips import counties_from_zip
import re
import programs.programs.messages as messages
from integrations.util import Cache


def calculate_child_care_assistance(screen, data, program):
    eligibility = eligibility_child_care_assistance(screen)
    value = value_child_care_assistance(screen)

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


def eligibility_child_care_assistance(screen):

    eligibility = {
        "eligible": True,
        "passed": [],
        "failed": []
    }

    # Family must have at least one child under 13 years old (19 years
    # old if special needs or disability).
    # county level income requirements
    # are working, seeking employment, or participating in training/education

    # CHILD TEST
    # todo: support children with special needs
    cccap_children = num_cccap_children(screen)

    if cccap_children < 1:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.child(min_age=0, max_age=13))
    else:
        eligibility["passed"].append(messages.child(min_age=0, max_age=13))

    # WORKING TEST
    # todo: support families seeking work

    # INCOME TEST
    counties = counties_from_zip(screen.zipcode)
    county_name = counties[0] if len(counties) > 0 else screen.county
    frequency = "yearly"
    cccap_county_data = cccap_county_values(county_name)
    if not cccap_county_data:
        eligibility["eligible"] = False
        eligibility["failed"].append(messages.location())
        return eligibility

    income_types = ['all']
    gross_income = screen.calc_gross_income(frequency, income_types)
    if cccap_children >= 1:
        income_limit = cccap_county_data[screen.household_size] * 12
        if gross_income > income_limit:
            eligibility["eligible"] = False
            eligibility["failed"].append(messages.income(gross_income, income_limit))
        else:
            eligibility["passed"].append(messages.income(gross_income, income_limit))

    return eligibility


def value_child_care_assistance(screen):
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
                household_member.has_disability():
            value += afterschool_value

    return value


def cccap_county_values(county_name):
    match = False
    sheet_values = cache.fetch()

    cccap_county_name = county_name.replace(" County", "")
    non_decimal = re.compile(r'[^\d.]+')

    for row in sheet_values:
        if row[0] == cccap_county_name:
            match = {
                1: -1,
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

    household_members = screen.household_members.all()
    for household_member in household_members:
        if household_member.age <= 12:
            children += 1
        elif household_member.age >= 13 and \
                household_member.age <= 19 and \
                household_member.has_disability():
            children += 1

    return children


class CCCAPCache(Cache):
    expire_time = 60 * 60 * 24
    default = ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0']

    def update(self):
        spreadsheet_id = '1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk'
        range_name = 'Sheet1!A14:J78'
        sheet_values = sheets_get_data(spreadsheet_id, range_name)
        if not sheet_values:
            raise Exception('Sheet unavailable')

        return sheet_values


cache = CCCAPCache()
