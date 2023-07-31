import programs.programs.messages as messages


def calculate_universal_preschool(screen, data, program):
    universal_preschool = UniversalPreschool(screen, program)
    eligibility = universal_preschool.eligibility
    value = universal_preschool.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class UniversalPreschool():
    qualifying_min_age = 3
    min_age = 4
    max_age = 5
    amount = {
        '10_hours': 4_837,
        '15_hours': 6_044,
        '30_hours': 10_655
    }

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
        '''
        If you make less than a certain income, or if there is a foster child
        then that child can be 3 years old, or if they are 4 or 5, then they can get twice as much UpreK
        '''
        foster_children = self.screen.num_children(age_min=UniversalPreschool.qualifying_min_age,
                                                   age_max=UniversalPreschool.max_age,
                                                   child_relationship=['fosterChild'])
        income_limit = int(2.7 * self.fpl[self.screen.household_size])
        self.income_requirement = self.screen.calc_gross_income('yearly', ['all']) < income_limit
        other_factors = self.income_requirement or foster_children >= 1

        # Has child
        children = self.screen.num_children(age_min=UniversalPreschool.min_age, age_max=UniversalPreschool.max_age)
        qualifying_children = self.screen.num_children(age_min=UniversalPreschool.qualifying_min_age,
                                                       age_max=UniversalPreschool.max_age)

        min_age = UniversalPreschool.qualifying_min_age if other_factors else UniversalPreschool.min_age

        self._condition(children >= 1 or (qualifying_children >= 1 and other_factors),
                        messages.child(min_age, UniversalPreschool.max_age))

    def calc_value(self):
        self.value = 0
        for child in self.screen.household_members.filter(age__range=(3, 5)):
            if child.relationship == 'fosterChild' or self.income_requirement:
                if child.age == 3:
                    self.value += UniversalPreschool.amount['10_hours']
                else:
                    self.value += UniversalPreschool.amount['30_hours']
            else:
                self.value += UniversalPreschool.amount['15_hours']

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
