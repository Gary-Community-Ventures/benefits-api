from .base import PolicyEngineMembersCalculator


class WIC(PolicyEngineMembersCalculator):
    wic_categories = {
        'NONE': 0,
        'INFANT': 130,
        'CHILD': 74,
        "PREGNANT": 100,
        "POSTPARTUM": 100,
        "BREASTFEEDING": 100,
    }
    pe_name = 'wic'

    def value(self):
        total = 0

        for _, pvalue in self.pe_data['people'].items():
            if pvalue[self.pe_name][self.year] > 0:
                total += self.wic_categories[pvalue['wic_category'][self.year]] * 12

        return total


class Medicaid(PolicyEngineMembersCalculator):
    pe_name = 'medicaid'

    co_child_medicaid_average = 200 * 12
    co_adult_medicaid_average = 310 * 12
    co_aged_medicaid_average = 170 * 12

    presumptive_amount = 74 * 12

    def value(self):
        total = 0

        for _, pvalue in self.pe_data['people'].items():
            # here we need to adjust for children as policy engine
            # just uses the average which skews very high for adults and
            # aged adults

            if pvalue['age'][self.year] <= 18:
                medicaid_estimated_value = self.co_child_medicaid_average
            elif pvalue['age'][self.year] > 18 and pvalue['age'][self.year] < 65:
                medicaid_estimated_value = self.co_adult_medicaid_average
            elif pvalue['age'][self.year] >= 65:
                medicaid_estimated_value = self.co_aged_medicaid_average
            else:
                medicaid_estimated_value = 0

            total += medicaid_estimated_value

        in_wic_demographic = False
        for member in self.screen.household_members.all():
            if member.pregnant is True or member.age <= 5:
                in_wic_demographic = True
        if total == 0 and in_wic_demographic:
            if self.screen.has_benefit('medicaid') is True \
                    or self.screen.has_benefit('tanf') is True \
                    or self.screen.has_benefit('snap') is True:
                total = self.presumptive_amount

        return total


class PellGrant(PolicyEngineMembersCalculator):
    pe_name = 'pell_grant'


class Ssi(PolicyEngineMembersCalculator):
    pe_name = 'ssi'


class AidToTheNeedyAndDisabled(PolicyEngineMembersCalculator):
    pe_name = 'co_state_supplement'


class OldAgePension(PolicyEngineMembersCalculator):
    pe_name = 'co_oap'


class Chp(PolicyEngineMembersCalculator):
    pe_name = 'co_chp'

    amount = 200 * 12

    def value(self):
        total = 0

        for _, pvalue in self.pe_data['people'].items():
            if pvalue['co_chp_eligible'][self.year] > 0 and self.screen.has_insurance_types(('none',)):
                total += self.amount

        return total
