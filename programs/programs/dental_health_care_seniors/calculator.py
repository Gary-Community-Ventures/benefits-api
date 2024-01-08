from programs.programs.calc import ProgramCalculator, Eligibility
import programs.programs.messages as messages


class DentalHealthCareSeniors(ProgramCalculator):
    amount = 80
    min_age = 60
    percent_of_fpl = 2.5
    dependencies = ['age', 'income_amount', 'income_frequency', 'insurance', 'household_size']

    def eligible(self) -> Eligibility:
        e = Eligibility()
        e.member_eligibility(
            self.screen.household_members.all(),
            [
                (
                    lambda m: m.insurance.has_insurance_types(('medicaid', 'private')),
                    messages.must_not_have_benefit('Medicaid')
                ),
                (
                    lambda m: m.age > DentalHealthCareSeniors.min_age,
                    messages.older_than(DentalHealthCareSeniors.min_age)
                )
            ]
        )

        # Income test
        fpl = self.program.fpl.as_dict()
        gross_income = int(self.screen.calc_gross_income("monthly", ["all"]))
        income_band = int(DentalHealthCareSeniors.percent_of_fpl * fpl[self.screen.household_size] / 12)
        e.condition(gross_income <= income_band,
                    messages.income(gross_income, income_band))

        return e

    def value(self):
        return DentalHealthCareSeniors.amount * self.screen.num_adults(age_max=DentalHealthCareSeniors.min_age) * 12
