from programs.programs.calc import Eligibility, ProgramCalculator


class UtilityBillPay(ProgramCalculator):
    presumptive_eligibility = ("snap", "ssi", "andcs", "tanf", "wic", "co_medicaid", "emergency_medicaid", "chp")
    amount = 400

    def household_eligible(self, e: Eligibility):
        # has other programs
        presumptive_eligible = False
        for benefit in UtilityBillPay.presumptive_eligibility:
            if self.screen.has_benefit(benefit):
                presumptive_eligible = True
            elif benefit in self.data and self.data[benefit].eligible:
                presumptive_eligible = True

        e.condition(presumptive_eligible)

        # has rent or mortgage expense
        has_rent_or_mortgage = self.screen.has_expense(["rent", "mortgage"])
        e.condition(has_rent_or_mortgage)
