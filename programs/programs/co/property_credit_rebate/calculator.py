from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class PropertyCreditRebate(ProgramCalculator):
    amount = 1044
    min_age = 65
    disabled_min_age = 18
    income_limit = {"single": 18_026, "married": 23_345}
    dependencies = ["age", "income_frequency", "income_amount", "relationship"]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Someone is disabled
        someone_disabled = False
        for member in self.screen.household_members.all():
            someone_disabled = someone_disabled or (
                member.has_disability() and member.age > PropertyCreditRebate.disabled_min_age
            )

        # Someone is old enough
        someone_old_enough = self.screen.num_adults(age_max=PropertyCreditRebate.min_age) >= 1

        e.condition(someone_disabled or someone_old_enough, messages.has_disability())

        e.condition(someone_disabled or someone_old_enough, messages.older_than(PropertyCreditRebate.min_age))

        # Income test
        relationship_status = "single"
        for member_id, married_to in self.screen.relationship_map().items():
            if married_to is not None:
                relationship_status = "married"

        gross_income = self.screen.calc_gross_income("yearly", ["all"])
        e.condition(
            gross_income <= PropertyCreditRebate.income_limit[relationship_status],
            messages.income(gross_income, PropertyCreditRebate.income_limit[relationship_status]),
        )

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        e.condition(has_rent_or_mortgage)

        return e
