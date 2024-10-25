from programs.programs import messages
from programs.programs.calc import Eligibility
import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Medicaid
from programs.programs.federal.pe.member import Wic
from screener.models import HouseholdMember


class NcMedicaid(Medicaid):
    medicaid_categories = {
        "NONE": 0,
        "ADULT": 512,  # * 12 = 6146,  Medicaid Expansion Adults
        "INFANT": 372,  # * 12 = 4464,  Medicaid for Children
        "YOUNG_CHILD": 372,  # * 12 = 4464,  Medicaid for Children
        "OLDER_CHILD": 372,  # * 12 = 4464,  Medicaid for Children
        "PREGNANT": 1045,  # * 12 = 12536, Medicaid for Pregnant Women
        "YOUNG_ADULT": 512,  # * 12 = 6146,  Medicaid Expansion Adults
        "PARENT": 0,
        "SSI_RECIPIENT": 0,
        "AGED": 1519,  # * 12 = 13035, Medicaid for the Aged
        "DISABLED": 1086,  # * 12 = 18227, Medicaid for the Disabled
    }

    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.NcStateCode,
        dependency.member.IsDisabledDependency,
    ]

    def member_value(self, member: HouseholdMember):
        if self.get_member_variable(member.id) <= 0:
            return 0

        medicaid_category = self.sim.value("people", str(member.id), "medicaid_category", self.pe_period)

        # In Policy Engine, senior and disabled are not included in the medicaid categories variable.
        # Instead, a separate variable is used to determine the medicaid eligiblity for a senior or disabled member.
        is_senior_or_disabled = self.sim.value(
            "people", str(member.id), "is_optional_senior_or_disabled_for_medicaid", self.pe_period
        )

        if is_senior_or_disabled:
            if member.has_disability():
                return self.medicaid_categories["DISABLED"] * 12
            elif member.age >= 65:
                return self.medicaid_categories["AGED"] * 12
        return self.medicaid_categories[medicaid_category] * 12


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
