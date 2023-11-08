import programs.programs.messages as messages


def calculate_property_credit_rebate(screen, data, program):
    cpcr = PropertyCreditRebate(screen)
    eligibility = cpcr.eligibility
    value = cpcr.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class PropertyCreditRebate():
    amount = 1044
    min_age = 65
    disabled_min_age = 18
    income_limit = {"single": 16925, "married": 22858}

    def __init__(self, screen):
        self.screen = screen

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

        self.calc_eligibility()

        self.calc_value()

    def calc_eligibility(self):
        # Someone is disabled
        someone_disabled = False
        for member in self.screen.household_members.all():
            someone_disabled = someone_disabled or (
                member.has_disability() and member.age > PropertyCreditRebate.disabled_min_age
            )

        # Someone is old enough
        someone_old_enough = self.screen.num_adults(age_max=PropertyCreditRebate.min_age) >= 1

        self._condition(someone_disabled or someone_old_enough,
                        messages.has_disability())

        self._condition(someone_disabled or someone_old_enough,
                        messages.older_than(PropertyCreditRebate.min_age))

        # Income test
        relationship_status = 'single'
        for member_id, married_to in self.screen.relationship_map().items():
            if married_to is not None:
                relationship_status = 'married'

        gross_income = self.screen.calc_gross_income('yearly', ['all'])
        self._condition(gross_income <= PropertyCreditRebate.income_limit[relationship_status],
                        messages.income(gross_income, PropertyCreditRebate.income_limit[relationship_status]))

    def calc_value(self):
        self.value = PropertyCreditRebate.amount

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
