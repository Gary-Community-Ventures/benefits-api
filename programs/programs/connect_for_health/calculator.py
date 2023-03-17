from django.conf import settings
from programs.programs.connect_for_health.tax_credit_value import tax_credit_by_county
import programs.programs.messages as messages


def calculate_connect_for_health(screen, data):
    cfhc = ConnectForHealth(screen, data)
    eligibility = cfhc.eligibility
    value = cfhc.value

    calculation = {
        'eligibility': eligibility,
        'value': value
    }

    return calculation


class ConnectForHealth():
    health_credit_value = 313

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
        # Medicade eligibility
        is_medicaid_eligible = False
        for benefit in self.data:
            if benefit["name_abbreviated"] == 'medicaid':
                is_medicaid_eligible = benefit["eligible"]
                break

        self._condition(not is_medicaid_eligible,
                        messages.must_not_have_benefit("Medicaid"))

        # Someone has no health insurance
        has_no_hi = self.screen.has_types_of_insurance(['none'])
        self._condition(has_no_hi,
                        messages.has_no_insurance())

        # Income
        income_band = int(settings.FPL2022[self.screen.household_size]/12 * 4)
        gross_income = int(self.screen.calc_gross_income('yearly', ("all",))/12)
        self._condition(gross_income < income_band,
                        messages.income(gross_income, income_band))

    def calc_value(self):
        # https://stackoverflow.com/questions/6266727/python-cut-off-the-last-word-of-a-sentence
        self.value = tax_credit_by_county[self.screen.county.rsplit(' ', 1)[0]] * 12

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
