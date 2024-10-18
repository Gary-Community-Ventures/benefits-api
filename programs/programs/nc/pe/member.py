import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid
from programs.programs.federal.pe.member import Wic
from screener.models import HouseholdMember


class NcMedicaid(Medicaid):
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.NcStateCode,
    ]

    subcategory_values = {
        'MAD': 18227,  # Medicaid for the Disabled
        'MAA': 13035,  # Medicaid for the Aged
        'MPW': 12536,  # Medicaid for Pregnant Women
        'MXP': 6146,   # Medicaid Expansion Adults
        'MIC': 4464,   # Medicaid for Children
    }

    subcategory_fpl_percentages = {
        'MIC': 211,
        'MPW': 196,
        'MXP': 133,
        'MAD': 100,
        'MAA': 100,
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
        fpl_percentage = self.subcategory_fpl_percentages.get(subcategory, 0)
        household_size = self.screen.household_size

        if member.pregnant:
            household_size += 1

        fpl = self.program.fpl
        income_limit = int(
            fpl_percentage * fpl.get_limit(household_size) / 100
        )

        gross_income = int(self.screen.calc_gross_income("yearly", ["all"]))
        return gross_income <= income_limit

    def member_value(self, member: HouseholdMember):
        subcategory = self.determine_subcategory(member)
        if subcategory:
            estimated_value = self.subcategory_values[subcategory]
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
