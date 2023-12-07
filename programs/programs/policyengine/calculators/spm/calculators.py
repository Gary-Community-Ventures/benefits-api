from .base import PolicyEngineSpmCalulator


class Snap(PolicyEngineSpmCalulator):
    dependencies = []
    pe_name = 'snap'

    def value(self):
        return self.get_data()[self.pe_name][self.format_month()]


class SchoolLunch(PolicyEngineSpmCalulator):
    dependencies = []
    pe_name = 'school_meal_daily_subsidy'

    def value(self):
        total = 0
        num_children = self.screen.num_children(3, 18)

        if self.get_data()[self.pe_name][self.year] > 0 and num_children > 0:
            if self.get_data()['school_meal_tier'][self.year] != 'PAID':
                total = 680 * num_children

        return total


class Tanf(PolicyEngineSpmCalulator):
    dependencies = []
    pe_name = 'co_tanf'


class Acp(PolicyEngineSpmCalulator):
    dependencies = []
    pe_name = 'acp'


class Lifeline(PolicyEngineSpmCalulator):
    dependencies = []
    pe_name = 'lifeline'
