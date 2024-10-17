import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid
from programs.programs.federal.pe.member import Wic
from screener.models import HouseholdMember


class NcMedicaid(Medicaid):
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.NcStateCode,
    ]

    medicaid_subcategory_values = {
        'MAD': 18227,  # Medicaid for the Disabled
        'MAA': 13035,  # Medicaid for the Aged
        'MIC': 4464,   # Medicaid for Children
        'MPW': 12536,  # Medicaid for Pregnant Women
        'EM': 6268,    # Emergency Medicaid for Labor and Delivery
        'MXP': 6146,   # Medicaid Expansion Adults
    }

    medicaid_subcategory_fpl_percentages = {
        'MAD': 100,
        'MAA': 100,
        'MPW': 196,
        'MXP': 138,
        'MIC': 211,
    }

    def determine_subcategory(self, member: HouseholdMember):
        if self.is_eligible_mad(member):
            return 'MAD'
        elif self.is_eligible_maa(member):
            return 'MAA'
        elif self.is_eligible_mpw(member):
            return 'MPW'
        elif self.is_eligible_mxp(member):
            return 'MXP'
        elif self.is_eligible_mic(member):
            return 'MIC'
        else:
            return None 

    def is_eligible_mad(self, member: HouseholdMember):
        return member.has_disability() and self.is_income_within_limit(member, 'MAD')

    def is_eligible_maa(self, member: HouseholdMember):
        return member.age >= 65 and self.is_income_within_limit(member, 'MAA')

    def is_eligible_mpw(self, member: HouseholdMember):
        return member.pregnant and self.is_income_within_limit(member, 'MPW')

    def is_eligible_mxp(self, member: HouseholdMember):
        return (
            19 <= member.age <= 64
            and not member.pregnant
            and not member.has_disability()
            and self.is_income_within_limit(member, 'MXP')
        )

    def is_eligible_mic(self, member: HouseholdMember):
        return member.age <= 18 and self.is_income_within_limit(member, 'MIC')

    def is_income_within_limit(self, member: HouseholdMember, subcategory: str):
        fpl_percentage = self.medicaid_subcategory_fpl_percentages.get(subcategory, 0)
        household_size = self.screen.household_size

        fpl = self.program.fpl
        print(f"fpl limit {fpl.get_limit(household_size)}")
        income_limit = int(
            fpl_percentage * fpl.get_limit(household_size) / 100
        )

        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))

        print(f"income limit {income_limit}")
        print(f"Gross income {gross_income}")
        return gross_income <= income_limit

    def member_value(self, member: HouseholdMember):
        subcategory = self.determine_subcategory(member)
        print(f"subcat {subcategory}")
        if subcategory:
            estimated_value = self.medicaid_subcategory_values[subcategory]
            print(f"subcat e value {estimated_value}")
            return estimated_value
        else:
            return 0


class NcWic(Wic):
    wic_categories = {
        "NONE": 0,
        "INFANT": 130,
        "CHILD": 26,
        "PREGNANT": 47,
        "POSTPARTUM": 47,
        "BREASTFEEDING": 52,
    }
    pe_inputs = [
        *Wic.pe_inputs,
        dependency.household.NcStateCode,
    ]
