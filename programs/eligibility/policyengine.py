import requests
import json

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
        }
    }

    benefit_data = policy_engine_calculate(screen)

    #WIC
    for pkey, pvalue in benefit_data['people'].items():
        if pvalue['wic']['2022'] > 0:
            eligibility['wic']['eligible'] = True
            eligibility['wic']['estimated_value'] += pvalue['wic']['2022']

    #SNAP
    if benefit_data['spm_units']['spm_unit']['snap']['2022'] > 0:
        eligibility['snap']['eligible'] = True
        eligibility['snap']['estimated_value'] = benefit_data['spm_units']['spm_unit']['snap']['2022']

    return eligibility

# PolicyEngine currently supports SNAP and WIC for CO
def policy_engine_calculate(screen):
    policy_engine_params = policy_engine_prepare_params(screen)
    response = requests.post(
        "https://policyengine.org/us/api/calculate",
        json = policy_engine_params
    ).json()

    return response

def policy_engine_prepare_params(screen):
    household_members = screen.household_members.all()
    policy_engine_params = {
        "snap_earned_income_deduction": 0,
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                    "members": []
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
                    "snap": {"2022": None },
                    "acp": {"2022": None },
                    "lifeline": {"2022": None}
                }
            }
        }
    }

    for household_member in household_members:
        member_id = str(household_member.id)
        policy_engine_params['household']['people'][member_id] = {
            "employment_income": {
                "2022": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment']))
            },
            "age": {
                "2022": household_member.age
            },
            "wic": {
                "2022": None
            }
        }

        policy_engine_params['household']['tax_units']['tax_unit']['members'].append(member_id)
        policy_engine_params['household']['families']['family']['members'].append(member_id)
        policy_engine_params['household']['households']['household']['members'].append(member_id)
        policy_engine_params['household']['spm_units']['spm_unit']['members'].append(member_id)

    return policy_engine_params