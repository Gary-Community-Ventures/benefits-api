from programs.programs.policyengine.calculators.base import PolicyEnigineCalulator


class PolicyEngineMembersCalculator(PolicyEnigineCalulator):
    tax_dependent = True

    def value(self):
        total = 0
        for pkey, pvalue in self.pe_data['people'].items():
            in_tax_unit = str(pkey) in self.pe_data['tax_units']['tax_unit']['members']

            # The following programs use income from the tax unit,
            # so we want to skip any members that are not in the tax unit.
            if not in_tax_unit and self.tax_dependent:
                continue

            pe_value = pvalue[self.pe_name][self.year]

            total += pe_value

        return total


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
            if pvalue[self.pe_name][self.pe_period] > 0:
                total += self.wic_categories[pvalue['wic_category'][self.pe_period]] * 12

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

            if pvalue['age'][self.pe_period] <= 18:
                medicaid_estimated_value = self.co_child_medicaid_average
            elif pvalue['age'][self.pe_period] > 18 and pvalue['age'][self.pe_period] < 65:
                medicaid_estimated_value = self.co_adult_medicaid_average
            elif pvalue['age'][self.pe_period] >= 65:
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
            if pvalue['co_chp_eligible'][self.pe_period] > 0 and self.screen.has_insurance_types(('none',)):
                total += self.amount

        return total
