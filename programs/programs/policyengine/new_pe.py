from screener.models import Screen
from .calculators import all_calculators, PolicyEnigineCalulator
from programs.programs.calc import Eligibility
from .calculators.dependencies import DependencyError
from typing import List
import requests
from .calculators import YEAR


def eligibility(screen: Screen):
    missing_dependencies = screen.missing_fields()
    valid_programs: dict[str, type[PolicyEnigineCalulator]] = []

    for name_abbr, Calculator in all_calculators.items():
        if missing_dependencies.has(Calculator.dependencies):
            continue

        valid_programs[name_abbr] = Calculator

    data = policy_engine_calculate(pe_input(screen, valid_programs.values()))

    all_eligibility = dict[str, Eligibility]
    for Calculator in valid_programs:
        calc = Calculator(screen, data)

        e = calc.eligible()
        e.value = calc.value()

        all_eligibility.append(e)

    return all_eligibility


def policy_engine_calculate(data):
    response = requests.post(
        "https://api.policyengine.org/us/calculate",
        json=data
    )
    data = response.json()
    return data


def pe_input(screen: Screen, programs: List[type[PolicyEnigineCalulator]]):
    '''
    Generate Policy Engine API request from the list of programs.
    '''
    raw_input = {
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                }
            },
            "families": {
                "family": {
                    "members": []
                }
            },
            "households": {
                "household": {
                    "state_code_str": {YEAR: "CO"},
                    "members": []
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": [],
                }
            },
            "marital_units": {}
        }
    }

    members = screen.members.all()
    relationship_map = screen.relationship_map()

    already_added = set()
    for member_1, member_2 in relationship_map.items():
        if member_1 in already_added or member_2 in already_added or member_1 is None or member_2 is None:
            continue

        marital_unit = (str(member_1), str(member_2))
        raw_input['household']['marital_units']['-'.join(marital_unit)] = {'members': marital_unit}
        already_added.add(member_1)
        already_added.add(member_2)

    for Program in programs:
        for Data in Program.pe_inputs + Program.pe_outputs:
            if not Data.member:
                data = Data(screen, members)
                value = Data.value()
                unit = raw_input["household"][data.unit][data.sub_unit]

                if data.field in unit:
                    if value != unit[data.field][Program.pe_period]:
                        raise DependencyError(data.field, value, unit[data.field][Program.pe_period])

                unit[data.field][Program.pe_period] = value
                continue

            for member in members:
                member_id = str(member.id)
                data = Data(screen, member)
                value = data.value()

                unit = raw_input["household"][data.unit][member_id]

                if data.field in unit:
                    if value != unit[data.field][Program.pe_period]:
                        raise DependencyError(data.field, value, unit[data.field][Program.pe_period])

                unit[data.field][Program.pe_period] = value

    return raw_input
