from programs.programs.calc import ProgramCalculator, Eligibility
from integrations.services.sheets import GoogleSheetsCache
from programs.co_county_zips import counties_from_zip
import programs.programs.messages as messages


class CccapFplCache(GoogleSheetsCache):
    sheet_id = "1otQxo_hZu2pS1_1EBsPLVKP9HYFCdcYWZKNM24dbjvg"
    range_name = "current FPL %!A2:B"
    default = {}

    def update(self):
        data = super().update()

        county_fpls = {r[0] + ' County': int(r[1]) for r in data}

        return county_fpls


class ChildCareAssistance(ProgramCalculator):
    preschool_value = 6000
    afterschool_value = 1700
    max_age_preschool = 4
    max_age_afterschool = 13
    max_age_afterschool_disabled = 19
    asset_limit = 1_000_000
    dependencies = ["age", "income_amount", "income_frequency", "zipcode", "household_size"]
    fpl_limits = CccapFplCache()

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # age
        cccap_children = self._num_cccap_children()

        e.condition(cccap_children > 0, messages.child(max_age=ChildCareAssistance.max_age_afterschool))

        cccap_county_limits = self.fpl_limits.fetch()

        # location
        counties = counties_from_zip(self.screen.zipcode)
        county_name = self.screen.county if self.screen.county is not None else counties[0]
        e.condition(county_name in cccap_county_limits, messages.location())

        # income
        frequency = "yearly"
        gross_income = self.screen.calc_gross_income(frequency, ["all"])
        deductions = self.screen.calc_expenses(frequency, ["childSupport"])
        net_income = gross_income - deductions
        fpl_percent = cccap_county_limits[county_name] / 100
        fpl = self.program.fpl.as_dict()
        income_limit = fpl[self.screen.household_size] * fpl_percent
        e.condition(net_income <= income_limit, messages.income(net_income, income_limit))

        # assets
        e.condition(
            self.screen.household_assets < ChildCareAssistance.asset_limit,
            messages.assets(ChildCareAssistance.asset_limit),
        )

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
                and household_member.age <= ChildCareAssistance.max_age_afterschool_disabled
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
                and household_member.age <= ChildCareAssistance.max_age_afterschool_disabled
                and household_member.has_disability()
            ):
                children += 1

        return children
