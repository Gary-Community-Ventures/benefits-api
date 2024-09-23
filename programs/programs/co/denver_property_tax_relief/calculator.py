from programs.co_county_zips import counties_from_screen, counties_from_zip
from programs.programs.calc import MemberEligibility, ProgramCalculator, Eligibility
from integrations.services.sheets import GoogleSheetsCache
import programs.programs.messages as messages
from screener.models import HouseholdMember


class DenverAmiCache(GoogleSheetsCache):
    sheet_id = "1ggXBCWybiThlaL2s2FErpTdS5vZ_gZBXYX6d98nTqho"
    range_name = "current AMI!B2:I2"
    default = [0, 0, 0, 0, 0, 0, 0, 0]

    def update(self):
        data = super().update()

        return [int(a.replace(",", "")) for a in data[0]]


class DenverPropertyTaxRelief(ProgramCalculator):
    amount = 252
    ami_percent_rental_single = 0.25
    ami_percent_rental_couple = 0.30
    ami_percent_mortgage = 0.60
    child_max_age = 17
    age_eligible = 65
    county = "Denver County"
    ami = DenverAmiCache()
    income_types = [
        "wages",
        "selfEmployment",
        "pension",
        "veteran",
        "unemployment",
        "investment",
        "cOSDisability",
        "rental",
        "alimony",
        "deferredComp",
        "workersComp",
        "boarder",
    ]
    mortgage_amount = 1_800
    rent_amount = 1_000
    dependencies = [
        "zipcode",
        "income_amount",
        "income_frequency",
        "income_type",
        "expense_type",
        "household_size",
        "age",
        "relationship",
    ]

    def household_eligible(self) -> Eligibility:
        e = Eligibility()

        # county
        counties = counties_from_screen(self.screen)
        e.condition(DenverPropertyTaxRelief.county in counties, messages.location())

        # has rent or mortgage expense
        has_rent = self.screen.has_expense(["rent"])
        has_mortgage = self.screen.has_expense(["mortgage"])
        e.condition(has_rent or has_mortgage)

        # income
        multiple_adults = self.screen.num_adults(DenverPropertyTaxRelief.child_max_age + 1) >= 2
        ami_percent = -1
        if has_rent and multiple_adults:
            ami_percent = DenverPropertyTaxRelief.ami_percent_rental_couple
        elif has_rent:
            ami_percent = DenverPropertyTaxRelief.ami_percent_rental_single
        elif has_mortgage:
            ami_percent = DenverPropertyTaxRelief.ami_percent_mortgage

        ami = DenverPropertyTaxRelief.ami.fetch()
        limit = ami[self.screen.household_size - 1] * ami_percent
        total_income = 0
        for member in self.screen.household_members.all():
            if member.is_head() or member.is_spouse():
                total_income += member.calc_gross_income("yearly", DenverPropertyTaxRelief.income_types)
        e.condition(total_income <= limit, messages.income(total_income, limit))

        return e

    def member_eligible(self, member: HouseholdMember) -> MemberEligibility:
        e = MemberEligibility(member)

        # head or spouse
        e.condition(member.is_head() or member.is_spouse())

        has_child = self.screen.num_children(age_max=DenverPropertyTaxRelief.child_max_age) > 0

        # other condition
        other_condition = False
        if self.screen.has_expense(["mortgage"]) and has_child:
            other_condition = True

        if member.age >= DenverPropertyTaxRelief.age_eligible:
            other_condition = True

        if member.disabled or self.screen.has_benefit("ssi") or self.screen.has_benefit("ssdi"):
            other_condition = True

        e.condition(other_condition)

        return e

    def household_value(self):
        if self.screen.has_expense(["mortgage"]):
            return DenverPropertyTaxRelief.mortgage_amount
        elif self.screen.has_expense(["rent"]):
            return DenverPropertyTaxRelief.rent_amount

        return 0
