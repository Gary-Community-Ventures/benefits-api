from screener.models import Screen, HouseholdMember
from typing import List


class PolicyEngineScreenInput:
    member = False
    unit = ''
    sub_unit = ''
    field = ''

    def __init__(self, screen: Screen, members: List[HouseholdMember], relationship_map):
        self.screen = screen
        self.members = members
        self.relationship_map = relationship_map

    def value(self):
        return None


class TaxUnit(PolicyEngineScreenInput):
    unit = 'tax_units'
    sub_unit = 'tax_unit'


class SpmUnit(PolicyEngineScreenInput):
    unit = 'spm_units'
    sub_unit = 'spm_unit'


class Member(PolicyEngineScreenInput):
    unit = 'people'
    member = True

    def __init__(self, screen: Screen, member: HouseholdMember, relationship_map):
        self.screen = screen
        self.member = member
        self.relationship_map = relationship_map

    def value(self):
        return None


class DependencyError(Exception):
    def __init__(self, field, value_1, value_2) -> None:
        super().__init__(f'Confilcting Policy Engine Dependencies in {field}: {value_1} and {value_2}')
