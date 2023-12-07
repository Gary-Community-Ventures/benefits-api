from screener.models import Screen
from programs.models import Program
from programs.calc import Eligibility, ProgramCalculator


class PolicyEnigineCalulator(ProgramCalculator):
    pe_name = ''
    pe_category = ''
    pe_sub_category = ''

    def __init__(self, screen: Screen, program: Program, data, pe_data, year, month):
        super.__init__(screen, program, data)
        self.pe_data = pe_data
        self.year = year
        self.month = month

    def eligible(self) -> Eligibility:
        e = Eligibility()

        if self.value() > 0:
            e.eligible = True

        return e

    def value(self):
        return self.pe_data[self.pe_category][self.pe_sub_category][self.pe_name][self.year]

    def get_data(self):
        return self.pe_data[self.pe_category][self.pe_sub_category]

    def format_month(self) -> str:
        return self.year + '-' + self.month
