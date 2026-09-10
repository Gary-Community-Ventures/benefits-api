"""CCDF."""

from screener.models import HouseholdMember
from programs.framework.pe_base import PolicyEngineMembersCalculator
import programs.framework.pe_dependencies as dependency


class Ccdf(PolicyEngineMembersCalculator, abstract=True):
    pe_name = "is_ccdf_eligible"
    pe_inputs = [
        dependency.spm.AssetsDependency,
        dependency.member.CcdfReasonCareEligibleDependency,
        dependency.member.EmploymentIncomeDependency,
        dependency.member.SelfEmploymentIncomeDependency,
        dependency.member.PensionIncomeDependency,
        dependency.member.InvestmentIncomeDependency,
        dependency.member.RentalIncomeDependency,
        dependency.member.MiscellaneousIncomeDependency,
    ]
    pe_outputs = [dependency.member.Ccdf]

    def child_care_cost(self, member: HouseholdMember) -> int:
        """A state's own child care cost for an eligible member. Subclasses must define it.

        `NotImplementedError`, not `NotImplemented` — the latter is a singleton constant,
        not an exception type, so raising it produced `TypeError: 'NotImplementedType'
        object is not callable` and never the message it carries."""
        raise NotImplementedError(f"{type(self).__name__} must define the 'child_care_cost' method")

    def member_value(self, member: HouseholdMember):
        if not self.get_member_variable(member.id):
            return 0

        return self.child_care_cost(member)
