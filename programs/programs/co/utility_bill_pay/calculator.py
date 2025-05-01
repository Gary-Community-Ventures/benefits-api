from programs.programs.calc import Eligibility, ProgramCalculator, MemberEligibility


class UtilityBillPay(ProgramCalculator):
    presumptive_eligibility = ("snap", "ssi", "andcs", "tanf", "wic", "chp")
    member_presumptive_eligibility = ("co_medicaid", "emergency_medicaid")
    amount = 400

    def household_eligible(self, e: Eligibility):
        # has other programs
        presumptive_eligible = False
        for benefit in self.presumptive_eligibility:
            if self.screen.has_benefit(benefit):
                presumptive_eligible = True
            elif benefit in self.data and self.data[benefit].eligible:
                presumptive_eligible = True

        e.condition(presumptive_eligible)

        # has rent or mortgage expense
        e.condition(self._has_expense())

    def member_eligible(self, e: MemberEligibility):
        member = e.member

        presumptive_eligible = False
        for benefit in self.member_presumptive_eligibility:
            if member.has_benefit(benefit):
                presumptive_eligible = True

        e.condition(presumptive_eligible)

    def _has_expense(self):
        return self.screen.has_expense(["rent", "mortgage"])
