import programs.programs.messages as messages


def calculate_dental_health_care_seniors(screen, data, program):
    cdhcs = DentalHealthCareSeniors(screen, program)
    eligibility = cdhcs.eligibility
    value = cdhcs.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class DentalHealthCareSeniors():
    amount = 80
    min_age = 60

    def __init__(self, screen, program):
        self.screen = screen
        self.fpl = program.fpl.as_dict()

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

        self.calc_eligibility()

        self.calc_value()

    def calc_eligibility(self):
        self._member_eligibility(
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
        gross_income = int(self.screen.calc_gross_income("monthly", ["all"]))
        income_band = int(2.5 * self.fpl[self.screen.household_size]/12)
        self._condition(gross_income <= income_band,
                        messages.income(gross_income, income_band))

    def calc_value(self):
        self.value = DentalHealthCareSeniors.amount * self.screen.num_adults(age_max=DentalHealthCareSeniors.min_age) * 12

    def _failed(self, msg):
        self.eligibility["eligible"] = False
        self.eligibility["failed"].append(msg)

    def _passed(self, msg):
        self.eligibility["passed"].append(msg)

    def _condition(self, condition, msg):
        if condition is True:
            self._passed(msg)
        else:
            self._failed(msg)

    def _member_eligibility(self, members, conditions):
        '''
        Filter out members that do not meet the condition and make eligibility messages
        '''
        if len(conditions) <= 0:
            return members

        [condition, message] = conditions.pop()
        eligible_members = list(filter(condition, members))
        if message:
            self._condition(len(eligible_members) >= 1, message)

        return self._member_eligibility(eligible_members, conditions)