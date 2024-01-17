from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class UniversalPreschool(ProgramCalculator):
    qualifying_min_age = 3
    min_age = 4
    max_age = 5
    percent_of_fpl = 2.7
    amount = {
        '10_hours': 4_837,
        '15_hours': 6_044,
        '30_hours': 10_655
    }
    dependencies = ['age', 'income_amount', 'income_frequency', 'relationship', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        foster_children = self.screen.num_children(
            age_min=UniversalPreschool.qualifying_min_age,
            age_max=UniversalPreschool.max_age,
            child_relationship=['fosterChild']
        )

        income_requirement = self._meets_income_requirement()
        other_factors = income_requirement or foster_children >= 1

        # Has child
        children = self.screen.num_children(age_min=UniversalPreschool.min_age, age_max=UniversalPreschool.max_age)
        qualifying_children = self.screen.num_children(
            age_min=UniversalPreschool.qualifying_min_age,
            age_max=UniversalPreschool.max_age
        )

        min_age = UniversalPreschool.qualifying_min_age if other_factors else UniversalPreschool.min_age

        e.condition(
            children >= 1 or (qualifying_children >= 1 and other_factors),
            messages.child(min_age, UniversalPreschool.max_age)
        )

        return e

    def value(self, eligible_members: int):
        value = 0
        income_requirement = self._meets_income_requirement()

        for child in self.screen.household_members.filter(
            age__range=(UniversalPreschool.qualifying_min_age, UniversalPreschool.max_age)
        ):
            if child.relationship == 'fosterChild' or income_requirement:
                if child.age == 3:
                    value += UniversalPreschool.amount['10_hours']
                else:
                    value += UniversalPreschool.amount['30_hours']
            else:
                value += UniversalPreschool.amount['15_hours']

        return value

    def _meets_income_requirement(self):
        fpl = self.program.fpl.as_dict()
        income_limit = int(UniversalPreschool.percent_of_fpl * fpl[self.screen.household_size])
        return self.screen.calc_gross_income('yearly', ['all']) < income_limit
