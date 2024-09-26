from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
import programs.programs.messages as messages


class PropertyCreditRebate(ProgramCalculator):
    amount = 1044
    min_age = 65
    disabled_min_age = 18
    expenses = ["rent", "mortgage"]
    income_limit = {"single": 18_026, "married": 23_345}
    dependencies = ["age", "income_frequency", "income_amount", "relationship"]

    def household_eligible(self, e: Eligibility):
        # Income test
        relationship_status = "single"
        for _, married_to in self.screen.relationship_map().items():
            if married_to is not None:
                relationship_status = "married"

        gross_income = self.screen.calc_gross_income("yearly", ["all"])
        e.condition(
            gross_income <= PropertyCreditRebate.income_limit[relationship_status],
            messages.income(gross_income, PropertyCreditRebate.income_limit[relationship_status]),
        )

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(PropertyCreditRebate.expenses)
        e.condition(has_rent_or_mortgage)

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # disabled
        someone_disabled = member.has_disability() and member.age > PropertyCreditRebate.disabled_min_age

        # age
        someone_old_enough = member.age >= PropertyCreditRebate.min_age

        e.condition(someone_disabled or someone_old_enough)
