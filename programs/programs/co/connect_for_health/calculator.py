from integrations.services.sheets.sheets import GoogleSheets
from integrations.util.cache import Cache
from programs.programs.calc import ProgramCalculator, Eligibility
from programs.programs.helpers import medicaid_eligible
import programs.programs.messages as messages


class CFHCache(Cache):
    expire_time = 60 * 60 * 24
    default = {}
    sheet_id = "1SuOhwX5psXsipMS_G5DE_f9jLS2qWxf6temxY445EQg"
    range_name = "current report"
    average_column = "Average Monthly Premium Tax Credit"
    county_column = "County\n(source here)"

    def update(self):
        data = GoogleSheets(self.sheet_id, self.range_name).data_by_column(self.county_column, self.average_column)

        return {row[self.county_column].strip() + " County": float(row[self.average_column]) for row in data}


class ConnectForHealth(ProgramCalculator):
    percent_of_fpl = 4
    dependencies = ["insurance", "income_amount", "income_frequency", "county", "household_size"]
    county_values = CFHCache()

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Medicade eligibility
        e.condition(not medicaid_eligible(self.data), messages.must_not_have_benefit("Medicaid"))

        # HH member has no insurace or private insurance
        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (lambda m: m.insurance.has_insurance_types(("none", "private")), messages.has_no_insurance()),
                (
                    lambda m: not m.insurance.has_insurance_types(("va",)),
                    messages.must_not_have_benefit("VA"),
                ),
            ],
        )
        print(e.eligible_member_count)

        # Income
        fpl = self.program.fpl.as_dict()
        income_band = int(fpl[self.screen.household_size] / 12 * ConnectForHealth.percent_of_fpl)
        gross_income = int(self.screen.calc_gross_income("yearly", ("all",)) / 12)
        e.condition(gross_income < income_band, messages.income(gross_income, income_band))

        return e

    def value(self, eligible_members: int):
        values = self.county_values.fetch()
        return int(values[self.screen.county] * 12 * eligible_members)
