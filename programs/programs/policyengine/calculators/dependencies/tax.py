from .base import TaxUnit
from .member import TaxUnitHeadDependency, TaxUnitSpouseDependency


class Eitc(TaxUnit):
    field = "eitc"


class Coeitc(TaxUnit):
    field = "co_eitc"


class RefundableCtc(TaxUnit):
    field = "refundable_ctc"


class NonRefundableCtc(TaxUnit):
    field = "non_refundable_ctc"


class Coctc(TaxUnit):
    field = "co_ctc"


# WARN: this does not take into account multiple tax units
class PellGrantPrimaryIncomeDependency(TaxUnit):
    field = "pell_grant_primary_income"

    def value(self):
        total = 0
        for member in self.screen.household_members.all():
            is_head = TaxUnitHeadDependency(self.screen, member, self.relationship_map).value()
            is_spouse = TaxUnitSpouseDependency(self.screen, member, self.relationship_map).value()
            if is_head or is_spouse:
                total += int(member.calc_gross_income("yearly", ["all"]))

        return total


# WARN: this does not take into account multiple tax units
class PellGrantDependentsInCollegeDependency(TaxUnit):
    field = "pell_grant_dependents_in_college"
    dependencies = ("student",)

    def value(self):
        pell_grant_dependents_in_college = 0
        for member in self.members:
            if member.student:
                pell_grant_dependents_in_college += 1

        return pell_grant_dependents_in_college
