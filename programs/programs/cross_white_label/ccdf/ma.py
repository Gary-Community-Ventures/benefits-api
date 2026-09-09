"""MA CCFA (configured as ``ma_ccdf``)."""

from programs.framework.pe_base import PolicyEngineSpmCalulator
from screener.models import HouseholdMember
import programs.framework.pe_dependencies as dependency


class MaCcdf(PolicyEngineSpmCalulator):
    """
    Massachusetts Child Care Financial Assistance (CCFA).

    Reads Massachusetts' own model, ``ma_ccfa_eligible``, rather than the federal CCDF
    passthrough it replaced. PolicyEngine is retiring the federal CCDF eligibility
    variables and this was their last consumer here; they also made us assert
    reason-for-care unconditionally, which the MA model tests for real.

    ``program_code`` stays ``ma_ccdf``: it keys the Program row, the ``has_ccdf``
    current-benefit field and every translation. Only the model behind it changed.

    Eligibility is PolicyEngine's; the value is ours. ``ma_ccfa`` itself is not adopted
    here -- it returns $0 for a household reporting no childcare expense, which is most
    of the people screening for a childcare subsidy, and it needs two inputs the screener
    never asks for (provider type and childcare hours per day). So the age table below
    stays, gated on PolicyEngine's answer.

    Known consequence of the swap: a disabled child aged 13 to 15 makes the unit eligible
    (CCFA's disabled age limit is 16) but draws $0, because the age table stops at 14.
    """

    program_code = "ma_ccdf"

    pe_name = "ma_ccfa_eligible"
    pe_inputs = [
        *dependency.ma_ccfa_income,
        dependency.spm.AssetsDependency,
        dependency.member.AgeDependency,
        dependency.member.TaxUnitDependentDependency,
        dependency.member.IsDisabledDependency,
        # Must be the MA subclass, not TotalHoursWorkedDependency: two dependencies
        # writing different values to one field cannot share a payload, and every other
        # MA program sends this one.
        dependency.member.MaTotalHoursWorkedDependency,
        dependency.member.PregnancyDependency,
        dependency.household.MaStateCodeDependency,
    ]
    pe_outputs = [
        dependency.spm.MaCcfaEligible,
        dependency.member.MaCcfaEligibleChild,
    ]

    cost_by_age = (
        # cost, age
        (23_191, 2),
        (21_125, 3),
        (16_572, 4.5),
        (12_632, 14),
    )

    def household_value(self):
        """Nothing at the household level.

        ``pe_name`` is a boolean, so the inherited ``int(self.get_variable())`` would add
        $1 to an eligible household's total.
        """
        return 0

    def member_value(self, member: HouseholdMember):
        if not self.get_variable():
            return 0

        if not self.get_member_dependency_value(dependency.member.MaCcfaEligibleChild, member.id):
            return 0

        return self.child_care_cost(member)

    def child_care_cost(self, member: HouseholdMember):
        age = member.fraction_age()

        for [cost, age_limit] in self.cost_by_age:
            if age < age_limit:
                return cost

        return 0
