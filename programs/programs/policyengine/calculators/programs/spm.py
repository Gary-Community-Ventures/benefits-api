from ..base import PolicyEnigineCalulator


class PolicyEngineSpmCalulator(PolicyEnigineCalulator):
    pe_category = 'spm_units'
    pe_sub_category = 'spm_unit'


class Snap(PolicyEngineSpmCalulator):
    pe_name = 'snap'

    def value(self):
        return self.get_data()[self.pe_name][self.pe_period]


class SchoolLunch(PolicyEngineSpmCalulator):
    pe_name = 'school_meal_daily_subsidy'

    def value(self):
        total = 0
        num_children = self.screen.num_children(3, 18)

        if self.get_data()[self.pe_name][self.pe_period] > 0 and num_children > 0:
            if self.get_data()['school_meal_tier'][self.pe_period] != 'PAID':
                total = 680 * num_children

        return total


class Tanf(PolicyEngineSpmCalulator):
    pe_name = 'co_tanf'


class Acp(PolicyEngineSpmCalulator):
    pe_name = 'acp'


class Lifeline(PolicyEngineSpmCalulator):
    pe_name = 'lifeline'
