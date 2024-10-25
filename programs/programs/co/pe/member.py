from programs.programs.policyengine.calculators.base import PolicyEngineMembersCalculator
from programs.programs.federal.pe.member import CommoditySupplementalFoodProgram, Medicaid
from programs.programs.federal.pe.member import Wic
import programs.programs.policyengine.calculators.dependencies as dependency
from screener.models import HouseholdMember


class CoMedicaid(Medicaid):
    child_medicaid_average = 200 * 12
    adult_medicaid_average = 310 * 12
    aged_medicaid_average = 170 * 12
    pe_inputs = [
        *Medicaid.pe_inputs,
        dependency.household.CoStateCode,
    ]


class AidToTheNeedyAndDisabled(PolicyEngineMembersCalculator):
    pe_name = "co_state_supplement"
    pe_inputs = [
        dependency.member.SsiCountableResourcesDependency,
        dependency.member.SsiReportedDependency,
        dependency.member.IsBlindDependency,
        dependency.member.IsDisabledDependency,
        dependency.member.SsiEarnedIncomeDependency,
        dependency.member.SsiUnearnedIncomeDependency,
        dependency.member.AgeDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.TaxUnitHeadDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.household.CoStateCode,
    ]
    pe_outputs = [dependency.member.Andcs]


class OldAgePension(PolicyEngineMembersCalculator):
    pe_name = "co_oap"
    pe_inputs = [
        dependency.member.SsiCountableResourcesDependency,
        dependency.member.SsiEarnedIncomeDependency,
        dependency.member.SsiUnearnedIncomeDependency,
        dependency.member.AgeDependency,
        dependency.member.TaxUnitSpouseDependency,
        dependency.member.TaxUnitHeadDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.household.CoStateCode,
    ]
    pe_outputs = [dependency.member.Oap]


class Chp(PolicyEngineMembersCalculator):
    pe_name = "co_chp"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.PregnancyDependency,
        dependency.member.ExpectedChildrenPregnancyDependency,
        dependency.household.CoStateCode,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.member.ChpEligible]

    amount = 200 * 12

    def member_value(self, member: HouseholdMember):
        chp_eligible = self.sim.value(self.pe_category, str(member.id), "co_chp_eligible", self.pe_period) > 0

        if chp_eligible and self.screen.has_insurance_types(("none",)):
            return self.amount

        return 0


class FamilyAffordabilityTaxCredit(PolicyEngineMembersCalculator):
    pe_name = "co_family_affordability_credit"
    pe_inputs = [
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.household.CoStateCode,
        dependency.member.TaxUnitSpouseDependency,
        *dependency.irs_gross_income,
    ]
    pe_outputs = [dependency.member.FamilyAffordabilityTaxCredit]


class CoWic(Wic):
    wic_categories = {
        "NONE": 0,
        "INFANT": 130,
        "CHILD": 79,
        "PREGNANT": 104,
        "POSTPARTUM": 88,
        "BREASTFEEDING": 121,
    }
    pe_inputs = [
        *Wic.pe_inputs,
        dependency.household.CoStateCode,
    ]


class EveryDayEats(CommoditySupplementalFoodProgram):
    amount = 600

    def member_value(self, member: HouseholdMember):
        ede_eligible = self.sim.value(self.pe_category, str(member.id), self.pe_name, self.pe_period) > 0

        if ede_eligible:
            return self.amount

        return 0
