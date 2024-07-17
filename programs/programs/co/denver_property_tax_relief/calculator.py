from programs.co_county_zips import counties_from_zip
from programs.programs.calc import ProgramCalculator, Eligibility
from integrations.services.sheets import GoogleSheetsCache
import programs.programs.messages as messages
from screener.models import HouseholdMember
import math


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

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # county
        if self.screen.county is not None:
            counties = [self.screen.county]
        else:
            counties = counties_from_zip(self.screen.zipcode)
        e.condition(DenverPropertyTaxRelief.county in counties, messages.location())

        # has rent or mortgage expense
        has_mortgage = self.screen.has_expense(["mortgage"])
        has_rent = self.screen.has_expense(["rent"])
        e.condition(has_mortgage or has_rent)

        has_child = self.screen.num_children(age_max=DenverPropertyTaxRelief.child_max_age) > 0

        def meets_one_condition(member: HouseholdMember):
            if has_mortgage and has_child:
                return True

            if member.age >= DenverPropertyTaxRelief.age_eligible:
                return True

            if member.disabled or self.screen.has_ssi or self.screen.has_ssdi:
                return True

            return False

        e.member_eligibility(
            self.screen.household_members, [(lambda m: m.is_head or m.is_spouse, None), (meets_one_condition, None)]
        )

        # income
        multiple_adults = self.screen.num_adults(DenverPropertyTaxRelief.child_max_age + 1) >= 2
        ami_percent = math.inf
        if has_rent and multiple_adults:
            ami_percent = DenverPropertyTaxRelief.ami_percent_rental_couple
        elif has_rent:
            ami_percent = DenverPropertyTaxRelief.ami_percent_rental_single
        elif has_mortgage:
            ami_percent = DenverPropertyTaxRelief.ami_percent_mortgage

        ami = DenverPropertyTaxRelief.ami.fetch()
        limit = ami[self.screen.household_size - 1] * ami_percent
        # TODO: use the right income types
        income = self.screen.calc_gross_income("yearly", ["all"])
        e.condition(income <= limit, messages.income(income, limit))

        return e
