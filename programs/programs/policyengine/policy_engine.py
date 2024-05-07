from screener.models import HouseholdMember, Screen
from .calculators import all_calculators, PolicyEngineCalulator
from programs.programs.calc import Eligibility
from programs.util import Dependencies
from .calculators.dependencies.base import DependencyError
from typing import List
import requests
from .calculators.constants import YEAR, PREVIOUS_YEAR


def calc_pe_eligibility(screen: Screen, missing_fields: Dependencies) -> dict[str, Eligibility]:
    valid_programs: dict[str, type[PolicyEngineCalulator]] = {}

    for name_abbr, Calculator in all_calculators.items():
        if not Calculator.can_calc(missing_fields):
            continue

        valid_programs[name_abbr] = Calculator

    if len(valid_programs.values()) == 0 or len(screen.household_members.all()) == 0:
        return {}

    data = policy_engine_calculate(pe_input(screen, valid_programs.values()))['result']

    all_eligibility: dict[str, Eligibility] = {}
    has_non_tax_unit_members = screen.has_members_ouside_of_tax_unit()
    for name_abbr, Calculator in valid_programs.items():
        calc = Calculator(screen, data)

        e = calc.eligible()
        e.value = calc.value()

        if Calculator.tax_unit_dependent and has_non_tax_unit_members:
            e.multiple_tax_units = True

        all_eligibility[name_abbr] = e.to_dict()

    return all_eligibility


def policy_engine_calculate(data):
    response = requests.post(
        "https://api.policyengine.org/us/calculate",
        json=data
    )
    data = response.json()
    return data


def pe_input(screen: Screen, programs: List[type[PolicyEngineCalulator]]):
    '''
    Generate Policy Engine API request from the list of programs.
    '''
    raw_input = {
        "household": {
            "people": {},
            "tax_units": {
                "tax_unit": {
                    "members": [],
                }
            },
            "families": {
                "family": {
                    "members": []
                }
            },
            "households": {
                "household": {
                    "state_code_str": {YEAR: "CO", PREVIOUS_YEAR: "CO"},
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
    members: list[HouseholdMember] = screen.household_members.all()
    relationship_map = screen.relationship_map()

    for member in members:
        member_id = str(member.id)
        household = raw_input['household']

        household['families']['family']['members'].append(member_id)
        household['households']['household']['members'].append(member_id)
        household['spm_units']['spm_unit']['members'].append(member_id)
        household['people'][member_id] = {}

        if member.is_in_tax_unit():
            household['tax_units']['tax_unit']['members'].append(member_id)

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
            period = Program.pe_period
            if hasattr(Program, 'pe_output_period') and Data in Program.pe_outputs:
                period = Program.pe_output_period

            if not Data.member:
                data = Data(screen, members, relationship_map)
                value = data.value()
                unit = raw_input["household"][data.unit][data.sub_unit]

                if data.field in unit and period in unit[data.field]:
                    if value != unit[data.field][period]:
                        raise DependencyError(data.field, value, unit[data.field][period])

                if data.field not in unit:
                    unit[data.field] = {}

                unit[data.field][period] = value
                continue

            for member in members:
                member_id = str(member.id)
                data = Data(screen, member, relationship_map)
                value = data.value()

                unit = raw_input["household"][data.unit][member_id]

                if data.field in unit and period in unit[data.field]:
                    if value != unit[data.field][period]:
                        raise DependencyError(data.field, value, unit[data.field][period])

                if data.field not in unit:
                    unit[data.field] = {}

                unit[data.field][period] = value

    return raw_input
