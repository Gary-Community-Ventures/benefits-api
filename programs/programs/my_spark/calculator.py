import programs.programs.messages as messages


def calculate_my_spark(screen, data, program):
    my_spark = MySpark(screen, data)
    eligibility = my_spark.eligibility
    value = my_spark.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class MySpark():
    amount_per_child = 1_000
    max_age = 14
    min_age = 11

    def __init__(self, screen, data):
        self.screen = screen
        self.data = data

        self.eligibility = {
            "eligible": True,
            "passed": [],
            "failed": []
        }

        self.calc_eligibility()

        self.calc_value()

    def calc_eligibility(self):
        # Qualify for FRL
        is_frl_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'nslp':
                is_frl_eligible = benefit["eligible"]
                break
        self._condition(is_frl_eligible, messages.must_have_benefit('Free or Reduced Lunch'))

        # Denever County
        self._condition(self.screen.county == 'Denver County', messages.location())

        # Kid 11 - 14
        in_age_range = False
        for member in self.screen.household_members.all():
            if self._between(member.age, MySpark.min_age, MySpark.max_age):
                in_age_range = True
        self._condition(in_age_range, messages.child(MySpark.min_age, MySpark.max_age))

    def calc_value(self):
        value = 0
        for member in self.screen.household_members.all():
            if self._between(member.age, MySpark.min_age, MySpark.max_age):
                value += MySpark.amount_per_child

        self.value = value

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

    def _between(self, value, min_val, max_val):
        return min_val <= value <= max_val
