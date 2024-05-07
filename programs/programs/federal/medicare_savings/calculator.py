from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class MedicareSavings(ProgramCalculator):
    valid_insurance = ("none", "employer", "private", "medicare")
    asset_limit = {
        "single": 10_930,
        "married": 17_130,
    }
    income_limit = {
        "single": 1_715,
        "married": 2_320,
    }
    min_age = 65
    amount = 175
    dependencies = [
        "household_assets",
        "relationship",
        "income_frequency",
        "income_amount",
        "age",
    ]

    def eligible(self) -> Eligibility:
        e = Eligibility()

        members = self.screen.household_members.all()

        def asset_limit(member):
            status = "married" if member.is_married()["is_married"] else "single"
            return self.screen.household_assets < MedicareSavings.asset_limit[status]

        def income_limit(member):
            is_married = member.is_married()
            if not is_married["is_married"]:
                status = "single"
                spouse_income = 0
            else:
                status = "married"
                spouse_income = is_married["married_to"].calc_gross_income(
                    "monthly", ("all",)
                )
            max_income = MedicareSavings.income_limit[status]
            income = member.calc_gross_income("monthly", ("all",)) + spouse_income
            return income < max_income

        e.member_eligibility(
            members,
            [
                (
                    lambda m: m.age >= MedicareSavings.min_age,
                    messages.older_than(MedicareSavings.min_age),
                ),
                (
                    lambda m: m.insurance.has_insurance_types(
                        MedicareSavings.valid_insurance
                    ),
                    messages.has_no_insurance(),
                ),
                (asset_limit, None),
                (income_limit, None),
            ],
        )

        return e

    def value(self, eligible_members: int):
        return MedicareSavings.amount * eligible_members * 12
