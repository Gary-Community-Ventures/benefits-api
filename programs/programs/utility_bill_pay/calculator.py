from programs.programs.calc import Eligibility, ProgramCalculator
import programs.programs.messages as messages


class UtilityBillPay(ProgramCalculator):
    income_limits = (
        36_983,
        48_362,
        59_742,
        71_122,
        82_501,
        93_881,
        96_014,
        101_120,
    )
    presumptive_eligibility = ('snap', 'ssi', 'andcs', 'tanf', 'wic')
    amount = 350
    dependencies = ['household_size', 'income_amount', 'income_frequency']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # is not eligible for LEAP
        is_leap_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'leap':
                is_leap_eligible = benefit["eligible"]
                break

        e.condition(not is_leap_eligible, messages.must_not_have_benefit('LEAP'))

        # has other programs
        presumptive_eligible = False
        for benefit in UtilityBillPay.presumptive_eligibility:
            if self.screen.has_benefit(benefit):
                presumptive_eligible = True

        e.condition(presumptive_eligible)

        # income
        income = int(self.screen.calc_gross_income('yearly', ['all']))
        income_limit = UtilityBillPay.income_limits[self.screen.household_size - 1]

        e.condition(income < income_limit, messages.income(income, income_limit))

        return e
