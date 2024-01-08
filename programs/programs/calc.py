from screener.models import Screen
from programs.models import Program
from programs.util import Dependencies


class Eligibility:
    def __init__(self):
        self.eligible = True
        self.pass_messages = []
        self.fail_messages = []
        self.value = 0
        self.eligible_member_count = 0

    def set_value(self, value):
        self.value = value

    def condition(self, passed: bool, message):
        if passed:
            self.passed(message)
        else:
            self.failed(message)

    def failed(self, msg):
        self.eligible = False
        self.fail_messages.append(msg)

    def passed(self, msg):
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
        return {
            "eligible": self.eligible and self.value > 0,
            "passed": self.pass_messages,
            "failed": self.fail_messages,
            "estimated_value": self.value,
        }


class ProgramCalculator:
    dependencies = tuple()

    def __init__(self, screen: Screen, program: Program, data):
        self.screen = screen
        self.program = program
        self.data = data

    def eligible(self) -> Eligibility:
        return Eligibility()

    def value(self, eligible_members: int):
        return 0

    def can_calc(self, missing_dependencies: Dependencies):
        return not missing_dependencies.has(self.dependencies)
