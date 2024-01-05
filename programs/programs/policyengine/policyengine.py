import requests
from programs.models import FederalPoveryLimit


def eligibility_policy_engine(screen):

    eligibility = {
        "wic": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "snap": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "nslp": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "eitc": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "ctc": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "coctc": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "coeitc": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "medicaid": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "ssi": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "tanf": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "andcs": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "oap": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "acp": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "lifeline": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "pell_grant": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
        "chp": {
            "eligible": False,
            "passed": [],
            "failed": [],
            "estimated_value": 0
        },
    }
    year = '2024'
    tax_year = '2023'
    snap_month = '2023-10'

    benefit_data = policy_engine_calculate(screen)['result']

    for pkey, pvalue in benefit_data['people'].items():
        wic_categories = {
            'NONE': 0,
            'INFANT': 130,
            'CHILD': 74,
            "PREGNANT": 100,
            "POSTPARTUM": 100,
            "BREASTFEEDING": 100,
        }
        # WIC
        if pvalue['wic'][year] > 0:
            eligibility['wic']['eligible'] = True
            eligibility['wic']['estimated_value'] += wic_categories[pvalue['wic_category'][year]] * 12

        in_tax_unit = str(pkey) in benefit_data['tax_units']['tax_unit']['members']

        # The following programs use income from the tax unit,
        # so we want to skip any members that are not in the tax unit.
        if not in_tax_unit:
            continue

        # MEDICAID
        if pvalue['medicaid'][year] > 0:
            eligibility['medicaid']['eligible'] = True

            # here we need to adjust for children as policy engine
            # just uses the average which skews very high for adults and
            # aged adults
            co_child_medicaid_average = 200 * 12
            co_adult_medicaid_average = 310 * 12
            co_aged_medicaid_average = 170 * 12

            if pvalue['age'][year] <= 18:
                medicaid_estimated_value = co_child_medicaid_average
            elif pvalue['age'][year] > 18 and pvalue['age'][year] < 65:
                medicaid_estimated_value = co_adult_medicaid_average
            elif pvalue['age'][year] >= 65:
                medicaid_estimated_value = co_aged_medicaid_average

            eligibility['medicaid']['estimated_value'] += medicaid_estimated_value

        # PELL GRANT
        if pvalue['pell_grant'][year] > 0:
            eligibility['pell_grant']['eligible'] = True
            eligibility['pell_grant']['estimated_value'] += pvalue['pell_grant'][year]

        # SSI
        if pvalue['ssi'][year] > 0:
            eligibility['ssi']['eligible'] = True
            eligibility['ssi']['estimated_value'] += pvalue['ssi'][year]

        # AND-CS
        if pvalue['co_state_supplement'][year] > 0:
            eligibility['andcs']['eligible'] = True
            eligibility['andcs']['estimated_value'] += pvalue['co_state_supplement'][year]

        # OAP
        if pvalue['co_oap'][year] > 0:
            eligibility['oap']['eligible'] = True
            eligibility['oap']['estimated_value'] += pvalue['co_oap'][year]

        # CHP+
        if pvalue['co_chp_eligible'][year] > 0 and screen.has_insurance_types(('none',)):
            eligibility['chp']['eligible'] = True
            eligibility['chp']['estimated_value'] += 200 * 12

    # WIC PRESUMPTIVE ELIGIBILITY
    in_wic_demographic = False
    for member in screen.household_members.all():
        if member.pregnant is True or member.age <= 5:
            in_wic_demographic = True
    if eligibility['wic']['eligible'] is False and in_wic_demographic:
        if screen.has_benefit('medicaid') is True \
                or screen.has_benefit('tanf') is True \
                or screen.has_benefit('snap') is True:
            eligibility['wic']['eligible'] = True
            eligibility['wic']['estimated_value'] = 74 * 12

    # SNAP
    if benefit_data['spm_units']['spm_unit']['snap'][snap_month] > 0:
        eligibility['snap']['eligible'] = True
        eligibility['snap']['estimated_value'] = benefit_data['spm_units']['spm_unit']['snap'][snap_month] * 12

    # NSLP
    num_children = screen.num_children(3, 18)
    if benefit_data['spm_units']['spm_unit']['school_meal_daily_subsidy'][year] > 0 and num_children > 0:
        if benefit_data['spm_units']['spm_unit']['school_meal_tier'][year] != 'PAID':
            eligibility['nslp']['eligible'] = True
            eligibility['nslp']['estimated_value'] = 120 * num_children

    # TANF
    if benefit_data['spm_units']['spm_unit']['co_tanf'][year] > 0:
        eligibility['tanf']['eligible'] = True
        eligibility['tanf']['estimated_value'] = benefit_data['spm_units']['spm_unit']['co_tanf'][year]

    # ACP
    if benefit_data['spm_units']['spm_unit']['acp'][year] > 0:
        eligibility['acp']['eligible'] = True
        eligibility['acp']['estimated_value'] = benefit_data['spm_units']['spm_unit']['acp'][year]

    # Lifeline
    if benefit_data['spm_units']['spm_unit']['lifeline'][year] > 0:
        eligibility['lifeline']['eligible'] = True
        eligibility['lifeline']['estimated_value'] = benefit_data['spm_units']['spm_unit']['lifeline'][year]

    tax_unit_data = benefit_data['tax_units']['tax_unit']

    # EITC
    if tax_unit_data['eitc'][tax_year] > 0:
        eligibility['eitc']['eligible'] = True
        eligibility['eitc']['estimated_value'] = tax_unit_data['eitc'][tax_year]

    # COEITC
    if tax_unit_data['co_eitc'][tax_year] > 0:
        eligibility['coeitc']['eligible'] = True
        eligibility['coeitc']['estimated_value'] = tax_unit_data['co_eitc'][tax_year]

    # CTC
    if tax_unit_data['ctc'][tax_year] > 0:
        eligibility['ctc']['eligible'] = True
        eligibility['ctc']['estimated_value'] = tax_unit_data['ctc'][tax_year]

    # CO Child Tax Credit
    if tax_unit_data['ctc'][tax_year] > 0 and screen.num_children(age_max=6):
        income_bands = {
            "single": [{"max": 25000, "percent": .6}, {"max": 50000, "percent": .3}, {"max": 75000, "percent": .1}],
            "maried": [{"max": 35000, "percent": .6}, {"max": 60000, "percent": .3}, {"max": 85000, "percent": .1}]
        }
        income = screen.calc_gross_income('yearly', ['all'])
        relationship_status = 'maried' if screen.is_joint() else 'single'
        multiplier = 0
        for band in income_bands[relationship_status]:
            # if the income is less than the band then set the multiplier and break out of the loop
            if income <= band['max']:
                multiplier = band['percent']
                break

        eligibility['coctc']['eligible'] = multiplier != 0
        eligibility['coctc']['estimated_value'] = tax_unit_data['ctc'][tax_year] * multiplier

    return eligibility


# PolicyEngine currently supports SNAP and WIC for CO
def policy_engine_calculate(screen):
    policy_engine_params = policy_engine_prepare_params(screen)
    response = requests.post(
        "https://api.policyengine.org/us/calculate",
        json=policy_engine_params
    )
    data = response.json()
    return data


# TODO: add medicical expense deduction for over 60 snap
def policy_engine_prepare_params(screen):
    year = '2024'
    tax_year = '2023'
    snap_month = '2023-10'

    household_members = screen.household_members.all()

    # We have to manually calculate SNAP gross eligibility as colorado uses
    # 200% vs the 130% used by policy engine
    fpl = FederalPoveryLimit.objects.get(year='THIS YEAR').as_dict()
    snap_gross_limit = 2 * fpl[screen.household_size]
    snap_gross_income = screen.calc_gross_income('yearly', ['all'])

    if snap_gross_income < snap_gross_limit:
        meets_snap_gross_income_test = True
    else:
        meets_snap_gross_income_test = False

    pell_grant_dependents_in_college = 0
    for member in household_members:
        if member.student:
            pell_grant_dependents_in_college += 1

    policy_engine_params = {
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                    "members": [],
                    "eitc": {tax_year: None},
                    "co_eitc": {tax_year: None},
                    "ctc": {tax_year: None},
                    "tax_unit_is_joint": {tax_year: screen.is_joint()},
                    "pell_grant_primary_income": {year: 0},
                    "pell_grant_dependents_in_college": {year: pell_grant_dependents_in_college},
                }
            },
            "families": {
                "family": {
                    "members": []
                }
            },
            "households": {
                "household": {
                    "state_code_str": {year: 'CO', tax_year: 'CO'},
                    "members": []
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": [],
                    "snap_child_support_deduction": {year: int(screen.calc_expenses("yearly", ["childSupport"]))},
                    "snap_dependent_care_deduction": {year: int(screen.calc_expenses("yearly", ["childCare", "dependentCare"]))},
                    "snap_earned_income": {year: screen.calc_gross_income('yearly', ['earned'])},
                    "snap_standard_deduction": {year: None},
                    "snap_net_income_pre_shelter": {year: None},
                    "snap_excess_shelter_expense_deduction": {year: None},
                    "housing_cost": {year: int(screen.calc_expenses("yearly", ["rent", "mortgage"]))},
                    "snap_assets": {year: int(screen.household_assets)},
                    "snap_gross_income": {year: int(snap_gross_income)},
                    "snap_net_income": {year: None},
                    "snap_deductions": {year: None},
                    "meets_snap_net_income_test": {year: None},
                    "meets_snap_gross_income_test": {year: meets_snap_gross_income_test},
                    "meets_snap_asset_test": {year: True},
                    "is_snap_eligible": {year: None},
                    "meets_snap_categorical_eligibility": {year: False},
                    "snap_utility_allowance": {year: None},
                    "has_heating_cooling_expense": {year: screen.has_expense(["heating", "cooling"])},
                    "has_phone_expense": {year: screen.has_expense(["telephone"])},
                    "utility_expense": {year: int(screen.calc_expenses("yearly", ["otherUtilities", "heating", "cooling"]))},
                    "snap_emergency_allotment": {year: 0},
                    "snap": {snap_month: None},
                    "acp": {year: None},
                    "school_meal_daily_subsidy": {year: None},
                    "school_meal_tier": {year: None},
                    "meets_school_meal_categorical_eligibility": {year: None},
                    "lifeline": {year: None},
                    "co_tanf_countable_gross_earned_income": {year: int(screen.calc_gross_income('yearly', ['earned']))},
                    "co_tanf_countable_gross_unearned_income": {year: int(screen.calc_gross_income('yearly', ['unearned']))},
                    "co_tanf": {year: None},
                    "co_tanf_grant_standard": {year: None},
                    "broadband_cost": {year: 500},
                }
            },
            "marital_units": {}
        }
    }

    relationship_map = screen.relationship_map()
    head_id = screen.get_head().id
    spouse_id = relationship_map[head_id]

    for household_member in household_members:
        member_id = str(household_member.id)

        member_earned_income = int(household_member.calc_gross_income('yearly', ['earned']))
        member_unearned_income = int(household_member.calc_gross_income('yearly', ['unearned']))
        member_all_income = int(household_member.calc_gross_income('yearly', ['all']))

        is_tax_unit_head = member_id == str(head_id)
        is_tax_unit_spouse = member_id == str(spouse_id)

        is_tax_unit_dependent = (
            household_member.age <= 18 or
            (household_member.student and household_member.age <= 23) or
            household_member.has_disability()
        ) and (
            member_all_income < screen.calc_gross_income('yearly', ['all']) / 2
        ) and (
            not (is_tax_unit_head or is_tax_unit_spouse)
        )

        ssi_assets = 0
        if household_member.age >= 19:
            ssi_assets = screen.household_assets / screen.num_adults()

        policy_engine_params['household']['people'][member_id] = {
            "employment_income": {
                year: int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment'])),
                tax_year: int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment']))
            },
            "age": {year: household_member.age, tax_year: household_member.age},
            "is_pregnant": {year: household_member.pregnant},
            "is_tax_unit_head": {year: is_tax_unit_head, tax_year: is_tax_unit_head},
            "is_tax_unit_spouse": {year: is_tax_unit_spouse, tax_year: is_tax_unit_spouse},
            "is_tax_unit_dependent": {year: is_tax_unit_dependent, tax_year: is_tax_unit_dependent},
            "wic_category": {year: None},
            "wic": {year: None},
            "medicaid": {year: None},
            "ssi": {year: None},
            "ssi_earned_income": {year: member_earned_income},
            "ssi_unearned_income": {year: member_unearned_income},
            "is_ssi_disabled": {year: household_member.has_disability()},
            "ssi_countable_resources": {year: int(ssi_assets)},
            "ssi_amount_if_eligible": {year: None},
            "co_state_supplement": {year: None},
            "co_oap": {year: None},
            "pell_grant": {year: None},
            "pell_grant_dependent_available_income": {year: member_all_income},
            "pell_grant_countable_assets": {year: int(screen.household_assets)},
            "cost_of_attending_college": {year: 22_288 * (household_member.age >= 16 and household_member.student)},
            "pell_grant_months_in_school": {year: 9},
            "co_chp_eligible": {year: None},
        }

        pe_household = policy_engine_params['household']
        if is_tax_unit_head or is_tax_unit_spouse:
            pe_household['tax_units']['tax_unit']['pell_grant_primary_income'][year] += member_all_income
        if household_member.pregnant:
            pe_household['people'][member_id]['is_pregnant'] = {year: True}
        if household_member.visually_impaired:
            pe_household['people'][member_id]['is_blind'] = {year: True}

        pe_household['families']['family']['members'].append(member_id)
        pe_household['households']['household']['members'].append(member_id)
        pe_household['spm_units']['spm_unit']['members'].append(member_id)

        if is_tax_unit_head or is_tax_unit_spouse or is_tax_unit_dependent:
            pe_household['tax_units']['tax_unit']['members'].append(member_id)

    already_added = set()
    for member_1, member_2 in relationship_map.items():
        if member_1 in already_added or member_2 in already_added or member_1 is None or member_2 is None:
            continue

        marital_unit = (str(member_1), str(member_2))
        policy_engine_params['household']['marital_units']['-'.join(marital_unit)] = {'members': marital_unit}
        already_added.add(member_1)
        already_added.add(member_2)

    return policy_engine_params
