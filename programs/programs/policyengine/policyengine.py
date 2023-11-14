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

    benefit_data = policy_engine_calculate(screen)['result']

    # WIC & MEDICAID & SSI
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
        if pvalue['wic']['2023'] > 0:
            eligibility['wic']['eligible'] = True
            eligibility['wic']['estimated_value'] += wic_categories[pvalue['wic_category']['2023']] * 12

        # MEDICAID
        if pvalue['medicaid']['2023'] > 0:
            eligibility['medicaid']['eligible'] = True

            # here we need to adjust for children as policy engine
            # just uses the average which skews very high for adults and
            # aged adults
            co_child_medicaid_average = 200 * 12
            co_adult_medicaid_average = 310 * 12
            co_aged_medicaid_average = 170 * 12

            if pvalue['age']['2023'] <= 18:
                medicaid_estimated_value = co_child_medicaid_average
            elif pvalue['age']['2023'] > 18 and pvalue['age']['2023'] < 65:
                medicaid_estimated_value = co_adult_medicaid_average
            elif pvalue['age']['2023'] >= 65:
                medicaid_estimated_value = co_aged_medicaid_average

            eligibility['medicaid']['estimated_value'] += medicaid_estimated_value

        # PELL GRANT
        if pvalue['pell_grant']['2023'] > 0:
            eligibility['pell_grant']['eligible'] = True
            eligibility['pell_grant']['estimated_value'] += pvalue['pell_grant']['2023']

        # SSI
        if pvalue['ssi']['2023'] > 0:
            eligibility['ssi']['eligible'] = True
            eligibility['ssi']['estimated_value'] += pvalue['ssi']['2023']

        # AND-CS
        if pvalue['co_state_supplement']['2023'] > 0:
            eligibility['andcs']['eligible'] = True
            eligibility['andcs']['estimated_value'] += pvalue['co_state_supplement']['2023']

        # OAP
        if pvalue['co_oap']['2023'] > 0:
            eligibility['oap']['eligible'] = True
            eligibility['oap']['estimated_value'] += pvalue['co_oap']['2023']

        # CHP+
        if pvalue['co_chp_eligible']['2023'] > 0 and screen.has_insurance_types(('none',)):
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
    if benefit_data['spm_units']['spm_unit']['snap']['2023'] > 0:
        eligibility['snap']['eligible'] = True
        eligibility['snap']['estimated_value'] = \
            benefit_data['spm_units']['spm_unit']['snap']['2023']

    # NSLP
    num_children = screen.num_children(3, 18)
    if benefit_data['spm_units']['spm_unit']['school_meal_daily_subsidy']['2023'] > 0 and num_children > 0:
        if benefit_data['spm_units']['spm_unit']['school_meal_tier']['2023'] != 'PAID':
            eligibility['nslp']['eligible'] = True
            eligibility['nslp']['estimated_value'] = 680 * num_children

    # TANF
    if benefit_data['spm_units']['spm_unit']['co_tanf']['2023'] > 0:
        eligibility['tanf']['eligible'] = True
        eligibility['tanf']['estimated_value'] = benefit_data['spm_units']['spm_unit']['co_tanf']['2023']

    # ACP
    if benefit_data['spm_units']['spm_unit']['acp']['2023'] > 0:
        eligibility['acp']['eligible'] = True
        eligibility['acp']['estimated_value'] = benefit_data['spm_units']['spm_unit']['acp']['2023']

    # Lifeline
    if benefit_data['spm_units']['spm_unit']['lifeline']['2023'] > 0:
        eligibility['lifeline']['eligible'] = True
        eligibility['lifeline']['estimated_value'] = benefit_data['spm_units']['spm_unit']['lifeline']['2023']

    tax_unit_data = benefit_data['tax_units']['tax_unit']

    # EITC
    if tax_unit_data['earned_income_tax_credit']['2023'] > 0:
        eligibility['eitc']['eligible'] = True
        eligibility['eitc']['estimated_value'] = tax_unit_data['earned_income_tax_credit']['2023']

    # COEITC
    if tax_unit_data['co_eitc']['2023'] > 0:
        eligibility['coeitc']['eligible'] = True
        eligibility['coeitc']['estimated_value'] = tax_unit_data['co_eitc']['2023']

    # CTC
    if tax_unit_data['ctc']['2023'] > 0:
        eligibility['ctc']['eligible'] = True
        eligibility['ctc']['estimated_value'] = tax_unit_data['ctc']['2023']

    # CO Child Tax Credit
    if tax_unit_data['ctc']['2023'] > 0 and screen.num_children(age_max=6):
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
        eligibility['coctc']['estimated_value'] = tax_unit_data['ctc']['2023'] * multiplier

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

    pell_grant_primary_income = 0
    pell_grant_dependents_in_college = 0
    for member in household_members:
        if member.relationship in ('headOfHousehold', 'spouse'):
            pell_grant_primary_income += int(member.calc_gross_income('yearly', ['all']))
        if member.student:
            pell_grant_dependents_in_college += 1

    policy_engine_params = {
        "snap_earned_income_deduction": 0,
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                    "members": [],
                    "earned_income_tax_credit": {"2023": None},
                    "co_eitc": {"2023": None},
                    "ctc": {"2023": None},
                    "tax_unit_is_joint": {"2023": screen.is_joint()},
                    "pell_grant_primary_income": {"2023": int(screen.calc_gross_income('yearly', ['all']))},
                    "pell_grant_dependents_in_college": {"2023": pell_grant_dependents_in_college},
                }
            },
            "families": {
                "family": {
                    "members": []
                }
            },
            "households": {
                "household": {
                    "state_code_str": {"2023": "CO"},
                    "members": []
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": [],
                    "snap_child_support_deduction": {"2023": int(screen.calc_expenses("yearly", ["childSupport"]))},
                    "snap_dependent_care_deduction": {"2023": int(screen.calc_expenses("yearly", ["childCare", "dependentCare"]))},
                    "snap_earned_income": {"2023": None},
                    "snap_earned_income_deduction": {"2023": int(snap_gross_income) * .2},
                    "snap_standard_deduction": {"2023": None},
                    "snap_net_income_pre_shelter": {"2023": None},
                    "snap_excess_shelter_expense_deduction": {"2023": None},
                    "housing_cost": {"2023": int(screen.calc_expenses("yearly", ["rent", "mortgage"]))},
                    "snap_assets": {"2023": int(screen.household_assets)},
                    "snap_gross_income": {"2023": int(snap_gross_income)},
                    "snap_net_income": {"2023": None},
                    "snap_deductions": {"2023": None},
                    "meets_snap_net_income_test": {"2023": None},
                    "meets_snap_gross_income_test": {"2023": meets_snap_gross_income_test},
                    "meets_snap_asset_test": {"2023": True},
                    "is_snap_eligible": {"2023": None},
                    "meets_snap_categorical_eligibility": {"2023": False},
                    "snap_utility_allowance": {"2023": None},
                    "has_heating_cooling_expense": {"2023": screen.has_expense(["heating", "cooling"])},
                    "has_phone_expense": {"2023": screen.has_expense(["telephone"])},
                    "utility_expense": {"2023": int(screen.calc_expenses("yearly", ["otherUtilities", "heating", "cooling"]))},
                    "snap_emergency_allotment": {"2023": 0},
                    "snap": {"2023": None},
                    "acp": {"2023": None},
                    "school_meal_daily_subsidy": {"2023": None},
                    "school_meal_tier": {"2023": None},
                    "meets_school_meal_categorical_eligibility": {"2023": None},
                    "lifeline": {"2023": None},
                    "co_tanf_countable_gross_earned_income": {"2023": int(screen.calc_gross_income('yearly', ['earned']))},
                    "co_tanf_countable_gross_unearned_income": {"2023": int(screen.calc_gross_income('yearly', ['unearned']))},
                    "co_tanf": {"2023": None},
                    "co_tanf_grant_standard": {"2023": None},
                    "co_tanf_countable_earned_income_grant_standard": {"2023": None},
                    "broadband_cost": {"2023": 500},
                }
            },
            "marital_units": {}
        }
    }

    for household_member in household_members:
        member_id = str(household_member.id)

        if household_member.relationship == "headOfHousehold":
            is_tax_unit_head = True
        else:
            is_tax_unit_head = False

        ssi_assets = 0
        if household_member.age >= 19:
            ssi_assets = screen.household_assets / screen.num_adults()

        policy_engine_params['household']['people'][member_id] = {
            "employment_income": {
                "2023": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment'])),
                "2022": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment']))
            },
            "age": {"2023": household_member.age, "2022": household_member.age},
            "is_pregnant": {"2023": household_member.pregnant},
            "is_tax_unit_head": {"2023": is_tax_unit_head, "2022": is_tax_unit_head},
            "wic_category": {"2023": None},
            "wic": {"2023": None},
            "medicaid": {"2023": None},
            "ssi": {"2023": None},
            "ssi_earned_income": {"2023": int(household_member.calc_gross_income('yearly', ['earned']))},
            "ssi_unearned_income": {"2023": int(household_member.calc_gross_income('yearly', ['unearned']))},
            "is_ssi_disabled": {"2023": household_member.disabled or household_member.visually_impaired},
            "ssi_countable_resources": {"2023": int(ssi_assets)},
            "ssi_amount_if_eligible": {"2023": None},
            "co_state_supplement": {"2023": None},
            "co_oap": {"2023": None},
            "pell_grant": {"2023": None},
            "pell_grant_dependent_available_income": {"2023": int(household_member.calc_gross_income('yearly', ['all']))},
            "pell_grant_countable_assets": {"2023": int(screen.household_assets)},
            "cost_of_attending_college": {"2023": 22_288 * (household_member.age >= 16 and household_member.student)},
            "pell_grant_months_in_school": {"2023": 9},
            "co_chp_eligible": {"2023": None},
        }

        if household_member.pregnant:
            policy_engine_params['household']['people'][member_id]['is_pregnant'] = {'2023': True}
        if household_member.visually_impaired:
            policy_engine_params['household']['people'][member_id]['is_blind'] = {'2023': True}
        # TODO: this check should use the SSI disabled income as determination
        # if household_member.disabled and household_member.age >= 18:
            # policy_engine_params['household']['people'][member_id]['is_ssi_disabled'] = {'2023': True}

        policy_engine_params['household']['tax_units']['tax_unit']['members'].append(member_id)
        policy_engine_params['household']['families']['family']['members'].append(member_id)
        policy_engine_params['household']['households']['household']['members'].append(member_id)
        policy_engine_params['household']['spm_units']['spm_unit']['members'].append(member_id)

    already_added = set()
    for member_1, member_2 in screen.relationship_map().items():
        if member_1 in already_added or member_2 in already_added:
            continue

        marital_unit = (str(member_1), str(member_2)) if member_2 is not None else (str(member_1),)
        policy_engine_params['household']['marital_units']['-'.join(marital_unit)] = {'members': marital_unit}
        already_added.add(member_1)
        already_added.add(member_2)

    return policy_engine_params
