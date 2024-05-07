from screener.models import Screen
from programs.util import Dependencies
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from programs.models import Program


class Eligibility:
    def __init__(self):
        self.eligible = True
        self.pass_messages = []
        self.fail_messages = []
        self.value = 0
        self.eligible_member_count = 0
        self.multiple_tax_units = False

    def condition(self, passed: bool, message=None):
        '''
        Uses a condition to update the pass fail messages and eligibility.
        '''

        if message is None:
            if not passed:
                self.eligible = False
            return

        if passed:
            self.passed(message)
        else:
            self.failed(message)

    def failed(self, msg):
        '''
        Mark eligibility as failed and add a message to `fail_messages`
        '''
        self.eligible = False
        self.fail_messages.append(msg)

    def passed(self, msg):
        '''
        Add a message to `pass_messages`
        '''
        self.pass_messages.append(msg)

    def member_eligibility(self, members, conditions):
        '''
        Filter out members that do not meet the condition and make eligibility messages
        '''
        if len(conditions) <= 0:
            self.eligible_member_count = len(members)
            return members

        [condition, message] = conditions.pop()
        eligible_members = list(filter(condition, members))

        if message:
            self.condition(len(eligible_members) >= 1, message)
        elif len(eligible_members) <= 0:
            self.eligible = False

        return self.member_eligibility(eligible_members, conditions)

    def to_dict(self):
        '''
        Return the eligibility as a dictionary
        '''
        return {
            "eligible": self.eligible,
            "passed": self.pass_messages,
            "failed": self.fail_messages,
            "estimated_value": self.value if self.eligible else 0,
            "multiple_tax_units": self.multiple_tax_units,
        }


class ProgramCalculator:
    '''
    Base class for all Programs
    '''
    dependencies = tuple()
    amount = 0
    tax_unit_dependent = False

    def __init__(self, screen: Screen, program: "Program", data):
        self.screen = screen
        self.program = program
        self.data = data

    def eligible(self) -> Eligibility:
        '''
        Returns the `Eligibility` object with whether or not the program is eligible
        '''
        return Eligibility()

    def value(self, eligible_members: int):
        '''
        Return the value of the program
        '''
        return self.amount

    @classmethod
    def can_calc(cls, missing_dependencies: Dependencies):
        '''
        Returns whether or not the program can be calculated with the missing dependencies
        '''
        return not missing_dependencies.has(*cls.dependencies)
