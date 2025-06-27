from programs.programs.calc import MemberEligibility, ProgramCalculator


class MedicareSavings(ProgramCalculator):
    eligible_insurance_types = ("none", "employer", "private", "medicare")
    asset_limit = {
        "single": 11_160,
        "married": 17_470,
    }
    min_age = 65
    member_amount = 175 * 12
    general_income_disregard = 20
    earned_income_disregard = 65
    min_income_percent = 1.2
    max_income_percent = 1.35
    dependencies = ["household_assets", "relationship", "income_frequency", "income_amount", "age"]

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        # age
        e.condition(member.age >= self.min_age)

        # insurance
        e.condition(member.insurance.has_insurance_types(self.eligible_insurance_types))

        # assets
        is_married = member.is_married()
        status = "married" if is_married["is_married"] else "single"
        e.condition(self.screen.household_assets < self.asset_limit[status])

        # income
        earned_income = member.calc_gross_income("monthly", ("earned",))
        unearned_income = member.calc_gross_income("monthly", ("unearned",))
        if status == "married":
            spouse = is_married["married_to"]
            earned_income += spouse.calc_gross_income("monthly", ("earned",))
            unearned_income += spouse.calc_gross_income("monthly", ("unearned",))

        # apply $20 general income disregard
        if total_unearned_income >= self.general_income_disregard:
            total_unearned_income -= self.general_income_disregard
        else:
            remaining_disregard = self.general_income_disregard - total_unearned_income
            total_unearned_income = 0
            total_earned_income -= remaining_disregard

        # apply $65 earned income disregard
        total_earned_income -= self.earned_income_disregard

        # halve remaining earned income
        total_earned_income /= 2

        countable_income = total_unearned_income + total_earned_income

        household_size = self.screen.household_size
        fpl = self.program.year.as_dict()[household_size]
        min_income = fpl * self.min_income_percent
        max_income = fpl * self.max_income_percent

        e.condition(min_income <= countable_income <= max_income)
