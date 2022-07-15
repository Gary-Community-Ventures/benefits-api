import requests
import json

def policy_engine_calculate(screen):
    policy_engine_params = policy_engine_prepare_params(screen)
    response = requests.post(
        "https://policyengine.org/us/api/calculate",
        json = policy_engine_params
    ).json()
    # WE ARE HERE, need to parse this response
    print(response)

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
                    "snap": {"2022": None}
                }
            }
        }
    }

    for household_member in household_members:
        member_id = str(household_member.id)
        policy_engine_params['household']['people'][member_id] = {
            "employment_income": {
                "2022": int(household_member.calc_gross_income('yearly', ['wages', 'selfEmployment']))
            }
        }

        policy_engine_params['household']['tax_units']['tax_unit']['members'].append(member_id)
        policy_engine_params['household']['families']['family']['members'].append(member_id)
        policy_engine_params['household']['households']['household']['members'].append(member_id)
        policy_engine_params['household']['spm_units']['spm_unit']['members'].append(member_id)

    return policy_engine_params