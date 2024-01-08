from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class MySpark(ProgramCalculator):
    amount_per_child = 1_000
    max_age = 14
    min_age = 11
    county = 'Denver County'
    dependencies = ['age', 'county']

    def eligible(self) -> Eligibility:
        e = Eligibility()

        # Qualify for FRL
        is_frl_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'nslp':
                is_frl_eligible = benefit["eligible"]
                break
        e.condition(is_frl_eligible, messages.must_have_benefit('Free or Reduced Lunch'))

        # Denever County
        e.condition(self.screen.county == MySpark.county, messages.location())

        # Kid 11 - 14
        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (
                    lambda m: m.age > MySpark.min_age and m.age < MySpark.max_age,
                    messages.child(MySpark.min_age, MySpark.max_age)
                )
            ]
        )

        return e

    def value(self, eligible_members: int):
        return MySpark.amount_per_child * eligible_members
