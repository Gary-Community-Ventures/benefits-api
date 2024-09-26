from programs.programs.calc import MemberEligibility, ProgramCalculator


class MedicareSavings(ProgramCalculator):
    eligible_insurance_types = ("none", "employer", "private", "medicare")
    asset_limit = {
        "single": 10_930,
        "married": 17_130,
    }
    income_limit = {
        "single": 1_715,
        "married": 2_320,
    }
    min_age = 65
    member_amount = 175 * 12
    dependencies = ["household_assets", "relationship", "income_frequency", "income_amount", "age"]

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age
        e.condition(member.age >= MedicareSavings.min_age)

        # insurance
        e.condition(member.insurance.has_insurance_types(MedicareSavings.eligible_insurance_types))

        # assets
        status = "married" if member.is_married()["is_married"] else "single"
        e.condition(self.screen.household_assets < MedicareSavings.asset_limit[status])

        # income
        is_married = member.is_married()
        if not is_married["is_married"]:
            status = "single"
            spouse_income = 0
        else:
            status = "married"
            spouse_income = is_married["married_to"].calc_gross_income("monthly", ("all",))
        max_income = MedicareSavings.income_limit[status]
        income = member.calc_gross_income("monthly", ("all",)) + spouse_income
        e.condition(income < max_income)
