from programs.programs.policyengine.policyengine import eligibility_policy_engine
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household
from django.conf import settings

class PolicyEngineTestCase(TestCase):
    def test_medicaid_single_parent_two_children(self):
        expected_fpl_value = {
            3: {
                'min': 10000,
                'max': 11000
            }
        }

        # medicaid
        # child_fpl_limit = 1.41*settings.FPL[3]
        fpl_limit = .66*settings.FPL[3]
        screen = create_single_parent_two_children_household(annual_income=fpl_limit)
        eligibility = eligibility_policy_engine(screen)
        self.assertTrue(eligibility['medicaid']['eligible'])
        self.assertTrue(expected_fpl_value[3]['min'] <= eligibility['medicaid']['estimated_value'] <= expected_fpl_value[3]['max'])