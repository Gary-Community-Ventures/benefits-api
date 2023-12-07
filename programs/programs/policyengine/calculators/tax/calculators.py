from .base import PolicyEngineTaxUnitCalulator


class Eitc(PolicyEngineTaxUnitCalulator):
    dependencies = []
    pe_name = 'eitc'


class Coeitc(PolicyEngineTaxUnitCalulator):
    dependencies = []
    pe_name = 'co_eitc'


class Ctc(PolicyEngineTaxUnitCalulator):
    dependencies = []
    pe_name = 'ctc'


class Coctc(PolicyEngineTaxUnitCalulator):
    dependencies = []
    pe_name = 'ctc'

    income_bands = {
        "single": [{"max": 25000, "percent": .6}, {"max": 50000, "percent": .3}, {"max": 75000, "percent": .1}],
        "maried": [{"max": 35000, "percent": .6}, {"max": 60000, "percent": .3}, {"max": 85000, "percent": .1}]
    }

    def value(self):
        income = self.screen.calc_gross_income('yearly', ['all'])
        relationship_status = 'maried' if self.screen.is_joint() else 'single'
        multiplier = 0
        for band in self.income_bands[relationship_status]:
            # if the income is less than the band then set the multiplier and break out of the loop
            if income <= band['max']:
                multiplier = band['percent']
                break

        return self.get_data()[self.pe_name][self.year] * multiplier
