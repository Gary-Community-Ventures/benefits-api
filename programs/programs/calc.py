from screener.models import Screen, HouseholdMember
from programs.util import Dependencies, DependencyError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from programs.models import Program


class MemberEligibility:
    def __init__(self, member: HouseholdMember) -> None:
        self.member = member
        self.eligible = True
        self.value = 0

    def condition(self, passed: bool):
        """
        Set eligibility to False if the condition does not pass
        """
        if not passed:
            self.eligible = False


class Eligibility:
    def __init__(self):
        self.eligible: bool = True
        self.pass_messages = []
        self.fail_messages = []
        self.eligible_members: list[MemberEligibility] = []
        self.value: int = 0
        self.eligible_member_count: int = 0
        self.multiple_tax_units: bool = False

    def condition(self, passed: bool, message=None):
        """
        Uses a condition to update the pass fail messages and eligibility.
        """

        if message is None:
            if not passed:
                self.eligible = False
            return

        if passed:
            self.passed(message)
        else:
            self.failed(message)

    def failed(self, msg):
        """
        Mark eligibility as failed and add a message to `fail_messages`
        """
        self.eligible = False
        self.fail_messages.append(msg)

    def passed(self, msg):
        """
        Add a message to `pass_messages`
        """
        self.pass_messages.append(msg)

    def add_member_eligibility(self, member_eligibility: MemberEligibility):
        """
        Store a members eligibility
        """
        self.eligible_members.append(member_eligibility)

    def member_eligibility(self, members, conditions):
        """
        Filter out members that do not meet the condition and make eligibility messages
        """
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
        """
        Return the eligibility as a dictionary
        """
        return {
            "eligible": self.eligible,
            "passed": self.pass_messages,
            "failed": self.fail_messages,
            "estimated_value": self.value if self.eligible else 0,
            "multiple_tax_units": self.multiple_tax_units,
        }


class ProgramCalculator:
    """
    Base class for all Programs
    """

    dependencies = tuple()
    amount = 0
    member_amount = 0

    def __init__(self, screen: Screen, program: "Program", data, missing_dependencies: Dependencies):
        self.screen = screen
        self.program = program
        self.data = data
        self.missing_dependencies = missing_dependencies

    def eligible(self) -> Eligibility:
        """
        Combine the eligibility for the household and the members
        """
        e = self.household_eligible()

        one_member_eligible = False
        for member in self.screen.household_members.all():
            member_eligibility = self.member_eligible(member)
            e.add_member_eligibility(member_eligibility)

            if member_eligibility.eligible:
                one_member_eligible = True

        e.condition(one_member_eligible)

        return e

    def household_eligible(self) -> Eligibility:
        """
        Returns the `Eligibility` object with whether or not the program is eligible
        """
        return Eligibility()

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        return MemberEligibility(member)

    def value(self, eligibility: Eligibility):
        """
        Update the eligibility with household and member values
        """
        total = 0
        if eligibility.eligible:
            total += self.household_value()

        for member_eligibility in eligibility.eligible_members:
            if member_eligibility.eligible:
                member_value = self.member_value(member_eligibility.member)
                member_eligibility.value = member_value
                total += member_value

        eligibility.value = total

    def household_value(self):
        """
        Return the value of the program
        """
        return self.amount

    def member_value(self, member: HouseholdMember):
        """
        An eligible household members eligibility
        """
        return self.member_amount

    def calc(self):
        """
        Calculate the eligibility and value for a screen
        """
        if not self.can_calc():
            raise DependencyError()

        eligibility = self.eligible()

        self.value(eligibility)

        return eligibility

    def can_calc(self):
        """
        Returns whether or not the program can be calculated with the missing dependencies
        """
        return not self.missing_dependencies.has(*self.dependencies)
