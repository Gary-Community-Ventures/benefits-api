from integrations.services.sheets.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_screen
from programs.programs.calc import Eligibility, ProgramCalculator


class AffordableResidentialEnergyIncomeLimitCache(GoogleSheetsCache):
    default = {}
    sheet_id = "1T4RSc9jXRV5kzdhbK5uCQXqgtLDWt-wdh2R4JVsK33o"  # same sheet as Energy Outreach Colorado
    range_name = "'current'!A2:I65"

    def update(self):
        data = super().update()

        return {d[0].strip() + " County": [int(v.replace(",", "")) for v in d[1:]] for d in data}


class AffordableResidentialEnergy(ProgramCalculator):
    amount = 0  # TODO: figure out value
    dependencies = ["household_size", "energy_calculator", "income_amount", "income_frequency"]
    electricity_providers = [
        "co-city-of-gunnison",
        "co-gunnison-county-electric-association",
        "co-la-plata-electric-association",
        # TODO: figure out Platte River
        "co-fort-collins-utilities",
        "co-loveland-water-and-power",
        "co-longmont-power-and-communications",
        "co-estes-park-power-and-communications",
        "co-xcel-energy",
    ]
    gas_providers = []  # TODO: figure out gas providers
    presumptive_eligibility = ["leap", "section_8", "co_tanf", "andcs", "oap", "co_snap", "co_wic"]
    income_limits = AffordableResidentialEnergyIncomeLimitCache()

    def household_eligible(self, e: Eligibility):
        # presumptive eligibility
        if self.screen.has_benefit_from_list(self.presumptive_eligibility):
            # assume eligibility if they are eligible for one of the presumptive eligibility programs
            return

        # income
        income = self.screen.calc_gross_income("yearly", ["all"])
        county = counties_from_screen(self.screen)[0]
        income_limit = self.income_limits[county][self.screen.household_size]
        e.condition(income < income_limit)

        # utility providers
        e.condition(self.screen.energy_calculator.has_utility_provider(self.electricity_providers + self.gas_providers))
