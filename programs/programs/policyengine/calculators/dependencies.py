from screener.models import Screen
from programs.models import Program


class PolicyEngineInput:
    def __init__(self, screen: Screen, program: Program):
        self.screen = screen
        self.program = program


class TaxUnit(PolicyEngineInput):
    unit = 'tax_units'


class SpmUnit(PolicyEngineInput):
    unit = 'spm_units'


class Member(PolicyEngineInput):
    unit = 'people'
