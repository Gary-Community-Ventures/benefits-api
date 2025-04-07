from programs.programs.policyengine.calculators.base import PolicyEngineMembersCalculator
import programs.programs.policyengine.calculators.dependencies as dependency
from programs.programs.federal.pe.member import Aca, Ccdf, Medicaid, Wic
from .spm import MaSnap, MaTafdc, MaEaedc
from screener.models import HouseholdMember


# NOTE: MassHealth is Medicaid in MA
class MaMassHealth(Medicaid):
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.MaStateCodeDependency,
    ]

    medicaid_categories = {
        "NONE": 0,
        "ADULT": 419,
        "INFANT": 239,
        "YOUNG_CHILD": 239,
        "OLDER_CHILD": 239,
        "PREGNANT": 419,
        "YOUNG_ADULT": 419,
        "PARENT": 419,
        "SSI_RECIPIENT": 419,
        "AGED": 185,
        "DISABLED": 419,
    }


# NOTE: MassHealth Limited is Emergency Medicaid in MA
class MaMassHealthLimited(Medicaid):
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.MaStateCodeDependency,
    ]

    medicaid_categories = {
        "NONE": 0,
        "ADULT": 0,
        "INFANT": 239,
        "YOUNG_CHILD": 239,
        "OLDER_CHILD": 239,
        "PREGNANT": 419,
        "YOUNG_ADULT": 0,
        "PARENT": 0,
        "SSI_RECIPIENT": 0,
        "AGED": 0,
        "DISABLED": 0,
    }


class MaAca(Aca):
    pe_inputs = [
        *Aca.pe_inputs,
        dependency.household.MaStateCodeDependency,
        dependency.household.MaCountyDependency,
    ]


class MaWic(Wic):
    wic_categories = {
        "NONE": 0,
        "INFANT": 186,
        "CHILD": 77,
        "PREGNANT": 107,
        # NOTE: guesses based off Colorado
        "POSTPARTUM": 91,
        "BREASTFEEDING": 124,
    }


class MaCcdf(Ccdf):
    cost_by_age = (
        # cost, age
        (22_813, 2),
        (20_535, 3),
        (16_254, 4.5),
        (11_942, 14),
    )

    def child_care_cost(self, member: HouseholdMember):
        age = member.fraction_age()

        for [cost, age_limit] in self.cost_by_age:
            if age < age_limit:
                return cost

        return 0


class MaMbta(PolicyEngineMembersCalculator):
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.IsDisabledDependency,
        *MaSnap.pe_inputs,
        *MaTafdc.pe_inputs,
        *MaMassHealth.pe_inputs,
        *MaEaedc.pe_inputs,
    ]
    pe_outputs = [
        dependency.member.MaMbtaProgramsEligible,
        dependency.member.MaMbtaAgeEligible,
        dependency.member.MaSeniorCharlieCardEligible,
        dependency.member.MaTapCharlieCardEligible,
    ]

    amount = 30

    def member_value(self, member: HouseholdMember):
        mbta_programs_eligible = self.get_member_dependency_value(dependency.member.MaMbtaProgramsEligible, member.id)
        mbta_age_eligible = self.get_member_dependency_value(dependency.member.MaMbtaAgeEligible, member.id)
        mbta_eligible = mbta_programs_eligible and mbta_age_eligible
        senior_charlie_eligible = self.get_member_dependency_value(
            dependency.member.MaSeniorCharlieCardEligible, member.id
        )
        tap_charlie_eligible = self.get_member_dependency_value(dependency.member.MaTapCharlieCardEligible, member.id)

        if mbta_eligible or tap_charlie_eligible or senior_charlie_eligible:
            return self.amount

        return 0
