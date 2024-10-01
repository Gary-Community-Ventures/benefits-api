from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages
import math
from screener.models import HouseholdMember, Screen
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from programs.models import Program


class Ssdi(ProgramCalculator):
    income_limit = 1_550
    income_limit_blind = 2_590
    amount = 1_537
    min_age = 18
    ineligible_relationships = ["fosterChild", "grandChild"]
    parent_relationships = ["spouse", "domesticPartner", "headOfHousehold"]
    dependencies = ["income_amount", "income_frequency", "household_size"]

    def __init__(self, screen: Screen, program: "Program", data):
        self.eligible_members = []
        super().__init__(screen, program, data)

    def eligible(self) -> Eligibility:
        e = Eligibility()

        lowest_income = math.inf
        cat_eligibile = 0

        def income_condition(member: HouseholdMember):
            nonlocal lowest_income
            nonlocal cat_eligibile

            income_limit = Ssdi.income_limit_blind if member.visually_impaired else Ssdi.income_limit
            member_income = member.calc_gross_income("monthly", ("all",))

            if member_income < lowest_income:
                lowest_income = member_income
                cat_eligibile += 1

            return member_income < income_limit

        self.eligible_members = e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.has_disability(), messages.has_disability()),
                (
                    lambda m: m.calc_gross_income("yearly", ("sSDisability",)) == 0,
                    messages.must_not_have_benefit("SSDI"),
                ),
                (income_condition, None),
                (lambda m: self._child_eligible(m) or m.age >= Ssdi.min_age, None),
            ],
        )

        if cat_eligibile > 0:
            e.passed(messages.income(lowest_income, Ssdi.income_limit))

        return e

    def value(self, eligible_members: int):
        child_value = 0
        adult_value = 0
        child_ssdi_value = (self._parents_with_disability_ssdi_value() or Ssdi.amount) / 2
        for member in self.eligible_members:
            if member.age >= Ssdi.min_age:
                adult_value += Ssdi.amount
            else:
                child_value += child_ssdi_value

        total_value = adult_value + min(child_value, Ssdi.amount / 2)

        return total_value * 12

    def _parents_with_disability_ssdi_value(self):
        total = 0
        for member in self.screen.household_members.all():
            if not self._is_parent_with_disability(member):
                continue
            total += member.calc_gross_income("monthly", ("sSDisability",))

        return total

    def _is_parent_with_disability(self, member: HouseholdMember):
        # min parent age
        if member.age < Ssdi.min_age:
            return False

        # parent relationship
        if member.relationship not in Ssdi.parent_relationships:
            return False

        # has disability
        if not member.has_disability():
            return False

        return True

    def _child_eligible(self, member: HouseholdMember):
        # child relationship
        if member.relationship in Ssdi.ineligible_relationships:
            return False

        # unmaried
        if member.is_married()["is_married"]:
            return False

        # parent must also have a disability
        for other_member in self.screen.household_members.all():
            if self._is_parent_with_disability(other_member):
                return True

        return False
