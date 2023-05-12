import programs.programs.messages as messages
from programs.sheets import sheets_get_data


def calculate_energy_assistance(screen, data, program):
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
    spreadsheet_id = '1W8WbJsb5Mgb4CUkte2SCuDnqigqkmaO3LC0KSfhEdGg'
    range_name = "'FFY 2023'!A2:F129"
    sheet_values = sheets_get_data(spreadsheet_id, range_name)
    if not sheet_values:
        return value
    data = [[row[0], row[5]] for row in sheet_values if row != []]
    for row in data:
        county = row[0].replace('Application County: ', '') + 'County'
        if county == screen.county:
            value = int(float(row[1].replace('$', '')))

    return value
