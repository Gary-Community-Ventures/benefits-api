import requests
import json
from decimal import Decimal


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
    }

    benefit_data = policy_engine_calculate(screen)

    #WIC & MEDICAID
    for pkey, pvalue in benefit_data['people'].items():
        #WIC
        if pvalue['wic']['2022'] > 0:
            eligibility['wic']['eligible'] = True
            eligibility['wic']['estimated_value'] += pvalue['wic']['2022']

        #MEDICAID
        if pvalue['medicaid']['2022'] > 0:
            eligibility['medicaid']['eligible'] = True
            eligibility['medicaid']['estimated_value'] += pvalue['medicaid']['2022']

    #SNAP
    if benefit_data['spm_units']['spm_unit']['snap']['2022'] > 0:
        eligibility['snap']['eligible'] = True
        eligibility['snap']['estimated_value'] = benefit_data['spm_units']['spm_unit']['snap']['2022']

    #NSLP
    household_members = screen.household_members.all()
    children = False
    for household_member in household_members:
        if household_member.age <= 18:
            children = True

    if benefit_data['spm_units']['spm_unit']['school_meal_daily_subsidy']['2022'] > 0 and children:
        eligibility['nslp']['eligible'] = True
        eligibility['nslp']['estimated_value'] = 160 * benefit_data['spm_units']['spm_unit']['school_meal_daily_subsidy']['2022']

    #EITC
    if benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2022'] > 0:
        eligibility['eitc']['eligible'] = True
        eligibility['eitc']['estimated_value'] = benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2022']

    #COEITC
    if benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2022'] > 0:
        eligibility['coeitc']['eligible'] = True
        eligibility['coeitc']['estimated_value'] = .15 * benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2022']

    #CTC
    if benefit_data['tax_units']['tax_unit']['ctc']['2022'] > 0:
        eligibility['ctc']['eligible'] = True
        eligibility['ctc']['estimated_value'] = benefit_data['tax_units']['tax_unit']['ctc']['2022']
    return eligibility

# PolicyEngine currently supports SNAP and WIC for CO
def policy_engine_calculate(screen):
    policy_engine_params = policy_engine_prepare_params(screen)
    response = requests.post(
        "https://policyengine.org/us/api/calculate",
        json = policy_engine_params
    )

    data = response.json()
    return data

# TODO: add medicical expense deduction for over 60 snap
def policy_engine_prepare_params(screen):
    household_members = screen.household_members.all()
    policy_engine_params = {
        "snap_earned_income_deduction": 0,
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                    "members": [],
                    "earned_income_tax_credit": {"2022": None},
                    "ctc": {"2022": None}
                }
            },
            "families": {
                "family": {
                    "members": []
                }
            },
            "households": {
                "household": {
                    "members": []
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": [],
                    "snap_child_support_deduction": {"2022": int(screen.calc_expenses("yearly", ["childSupport"]))},
                    "snap_dependent_care_deduction": {"2022": int(screen.calc_expenses("yearly", ["childCare", "dependentCare"]))},
                    "snap_excess_shelter_expense_deduction": {"2022": int(screen.calc_expenses("yearly", ["rent", "mortgage"]) * 12) },
                    "snap_assets": {"2022": int(screen.household_assets) },
                    "snap": {"2022": None },
                    "acp": {"2022": None },
                    "school_meal_daily_subsidy": {"2022": None},
                    "lifeline": {"2022": None},
                }
            }
        }
    }

    for household_member in household_members:
        member_id = str(household_member.id)

        if household_member.relationship == "headOfHousehold":
            is_tax_unit_head = True
        else:
            is_tax_unit_head = False

        policy_engine_params['household']['people'][member_id] = {
            "employment_income": {
                "2022": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment']))
            },
            "age": { "2022": household_member.age },
            "is_tax_unit_head": { "2022": is_tax_unit_head },
            "wic": { "2022": None },
            "medicaid": {"2022": None }
        }

        if household_member.pregnant:
            policy_engine_params['household']['people'][member_id]['is_pregnant'] = {'2022': True}
        if household_member.visually_impaired:
            policy_engine_params['household']['people'][member_id]['is_blind'] = {'2022': True}
        if household_member.disabled:
            policy_engine_params['household']['people'][member_id]['is_ssi_disabled'] = {'2022': True}

        policy_engine_params['household']['tax_units']['tax_unit']['members'].append(member_id)
        policy_engine_params['household']['families']['family']['members'].append(member_id)
        policy_engine_params['household']['households']['household']['members'].append(member_id)
        policy_engine_params['household']['spm_units']['spm_unit']['members'].append(member_id)

    return policy_engine_params