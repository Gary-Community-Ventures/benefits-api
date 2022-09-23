import requests
import json
from decimal import Decimal
from django.conf import settings

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

            # here we need to adjust for children as policy engine just uses the average
            # which skews very high for adults and aged adults
            co_child_medicaid_average = 200*12
            co_adult_medicaid_average = 310*12
            co_aged_medicaid_average = 170*12

            if pvalue['age']['2022'] <= 18:
                medicaid_estimated_value = co_child_medicaid_average
            elif pvalue['age']['2022'] > 18 and pvalue['age']['2022'] < 65:
                medicaid_estimated_value = co_adult_medicaid_average
            elif pvalue['age']['2022'] >= 65:
                medicaid_estimated_value = co_aged_medicaid_average

            eligibility['medicaid']['estimated_value'] += medicaid_estimated_value

    #SNAP
    if benefit_data['spm_units']['spm_unit']['snap']['2022'] > 0:
        eligibility['snap']['eligible'] = True
        eligibility['snap']['estimated_value'] = benefit_data['spm_units']['spm_unit']['snap']['2022']

    #NSLP
    household_members = screen.household_members.all()
    num_children = screen.num_children(3, 18)
    if benefit_data['spm_units']['spm_unit']['school_meal_daily_subsidy']['2022'] > 0 and num_children > 0:
        if benefit_data['spm_units']['spm_unit']['school_meal_tier']['2022'] != 'PAID':
            eligibility['nslp']['eligible'] = True
            eligibility['nslp']['estimated_value'] = 680 * num_children

    #EITC
    if benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2021'] > 0:
        eligibility['eitc']['eligible'] = True
        eligibility['eitc']['estimated_value'] = benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2021']

    #COEITC
    if benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2021'] > 0:
        eligibility['coeitc']['eligible'] = True
        eligibility['coeitc']['estimated_value'] = .10 * benefit_data['tax_units']['tax_unit']['earned_income_tax_credit']['2021']

    #CTC
    if benefit_data['tax_units']['tax_unit']['ctc']['2021'] > 0:
        eligibility['ctc']['eligible'] = True
        for pkey, pvalue in benefit_data['people'].items():
            if pvalue['age']['2021'] <= 5:
                eligibility['ctc']['estimated_value'] += 3600
            elif pvalue['age']['2021'] > 5 and pvalue['age']['2021'] <= 17:
                eligibility['ctc']['estimated_value'] += 3000
        # eligibility['ctc']['estimated_value'] = benefit_data['tax_units']['tax_unit']['ctc']['2021']
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

    # We have to manually calculate SNAP gross eligibility as colorado uses 200% vs the 130% used by policy engine
    snap_gross_limit = 2 * settings.FPL2021[screen.household_size]
    snap_gross_income = screen.calc_gross_income('yearly', ['wages', 'selfEmployment', 'unemployment', 'childSupport', 'disabilityMedicaid', 'sSI', 'sSDependent', 'sSDisability', 'sSSurvivor', 'sSRetirement', 'cOSDisability', 'veteran', 'pension', 'deferredComp', 'workersComp', 'alimony', 'boarder', 'gifts', 'rental', 'investment'])

    if snap_gross_income < snap_gross_limit:
        meets_snap_gross_income_test = True
    else:
        meets_snap_gross_income_test = False

    policy_engine_params = {
        "snap_earned_income_deduction": 0,
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                    "members": [],
                    "earned_income_tax_credit": {"2021": None},
                    "ctc": {"2021": None},
                    "tax_unit_is_joint": {"2021": screen.is_joint()}
                }
            },
            "families": {
                "family": {
                    "members": []
                }
            },
            "households": {
                "household": {
                    "state_code_str": {"2022": "CO"},
                    "members": []
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": [],
                    "snap_child_support_deduction": {"2022": int(screen.calc_expenses("yearly", ["childSupport"]))},
                    "snap_dependent_care_deduction": {"2022": int(screen.calc_expenses("yearly", ["childCare", "dependentCare"]))},
                    "snap_excess_shelter_expense_deduction": {"2022": int(screen.calc_expenses("yearly", ["rent", "mortgage"])) },
                    "snap_assets": {"2022": int(screen.household_assets) },
                    "snap_gross_income": {"2022": int(snap_gross_income) },
                    "meets_snap_net_income_test": {"2022": None },
                    "meets_snap_gross_income_test": {"2022": meets_snap_gross_income_test },
                    "meets_snap_asset_test": {"2022": True},
                    "is_snap_eligible": {"2022": None},
                    "meets_snap_categorical_eligibility": {"2022": False},
                    "snap": {"2022": None },
                    "acp": {"2022": None },
                    "school_meal_daily_subsidy": {"2022": None},
                    "school_meal_tier": {"2022": None},
                    "meets_school_meal_categorical_eligibility": {"2022": None},
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
                "2022": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment'])),
                "2021": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment']))
            },
            "age": { "2022": household_member.age, "2021": household_member.age },
            "is_tax_unit_head": { "2022": is_tax_unit_head, "2021": is_tax_unit_head },
            "wic": { "2022": None },
            "medicaid": {"2022": None }
        }

        if household_member.pregnant:
            policy_engine_params['household']['people'][member_id]['is_pregnant'] = {'2022': True}
        if household_member.visually_impaired:
            policy_engine_params['household']['people'][member_id]['is_blind'] = {'2022': True}
        # TODO: this check should use the SSI disabled income as determination
        # if household_member.disabled and household_member.age >= 18:
            # policy_engine_params['household']['people'][member_id]['is_ssi_disabled'] = {'2022': True}

        policy_engine_params['household']['tax_units']['tax_unit']['members'].append(member_id)
        policy_engine_params['household']['families']['family']['members'].append(member_id)
        policy_engine_params['household']['households']['household']['members'].append(member_id)
        policy_engine_params['household']['spm_units']['spm_unit']['members'].append(member_id)

    return policy_engine_params