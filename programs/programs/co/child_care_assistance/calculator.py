from programs.programs.calc import ProgramCalculator, Eligibility
from integrations.services.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_zip
import re
import programs.programs.messages as messages


class CCCAPCache(GoogleSheetsCache):
    sheet_id = "1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk"
    range_name = "Sheet1!A14:J78"


class ChildCareAssistance(ProgramCalculator):
    preschool_value = 6000
    afterschool_value = 1700
    max_age_preschool = 4
    max_age_afterschool = 13
    max_age_afterschool_disabled = 19
    dependencies = [
        "age",
        "income_amount",
        "income_frequency",
        "zipcode",
        "household_size",
    ]
    county_values = CCCAPCache()

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # age
        cccap_children = self._num_cccap_children()

        e.condition(
            cccap_children > 0,
            messages.child(max_age=ChildCareAssistance.max_age_afterschool),
        )

        # location
        counties = counties_from_zip(self.screen.zipcode)
        county_name = counties[0] if len(counties) > 0 else self.screen.county
        cccap_county_data = self._cccap_county_values(county_name)
        e.condition(bool(cccap_county_data), messages.location())

        # income
        frequency = "yearly"
        income_types = ["all"]
        gross_income = self.screen.calc_gross_income(frequency, income_types)
        if cccap_county_data:
            income_limit = cccap_county_data[self.screen.household_size] * 12
            e.condition(
                gross_income < income_limit, messages.income(gross_income, income_limit)
            )
        else:
            e.eligible = False

        return e

    def value(self, eligible_members: int):
        value = 0

        household_members = self.screen.household_members.all()
        for household_member in household_members:
            if household_member.age <= ChildCareAssistance.max_age_preschool:
                value += ChildCareAssistance.preschool_value
            elif household_member.age < ChildCareAssistance.max_age_afterschool:
                value += ChildCareAssistance.afterschool_value
            elif (
                household_member.age >= ChildCareAssistance.max_age_afterschool
                and household_member.age
                <= ChildCareAssistance.max_age_afterschool_disabled
                and household_member.has_disability()
            ):
                value += ChildCareAssistance.afterschool_value

        return value

    def _num_cccap_children(self):
        children = 0

        household_members = self.screen.household_members.all()
        for household_member in household_members:
            if household_member.age < ChildCareAssistance.max_age_afterschool:
                children += 1
            elif (
                household_member.age >= ChildCareAssistance.max_age_afterschool
                and household_member.age
                <= ChildCareAssistance.max_age_afterschool_disabled
                and household_member.has_disability()
            ):
                children += 1

        return children

    def _cccap_county_values(self, county_name):
        match = False
        sheet_values = self.county_values.fetch()

        cccap_county_name = county_name.replace(" County", "")
        non_decimal = re.compile(r"[^\d.]+")

        for row in sheet_values:
            if row[0] == cccap_county_name:
                match = {
                    1: -1,
                    2: float(non_decimal.sub("", row[2])),
                    3: float(non_decimal.sub("", row[3])),
                    4: float(non_decimal.sub("", row[4])),
                    5: float(non_decimal.sub("", row[5])),
                    6: float(non_decimal.sub("", row[6])),
                    7: float(non_decimal.sub("", row[7])),
                    8: float(non_decimal.sub("", row[8])),
                    9: float(non_decimal.sub("", row[9])),
                }

        return match
