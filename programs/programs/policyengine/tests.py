from programs.programs.policyengine.policyengine import eligibility_policy_engine
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household
from django.conf import settings

class PolicyEngineTestCase(TestCase):
    def test_medicaid_single_parent_two_children(self):
        average_fpl_value = {
            3: {
                'min': 25000,
                'max': 26000
            }
        }

        # todo -- how do we manage income bands and household sizes to validate estimates...
        fpl_23 = .23*settings.FPL[3]
        screen = create_single_parent_two_children_household(annual_income=fpl_23)
        eligibility = eligibility_policy_engine(screen)
        self.assertTrue(eligibility['medicaid']['eligible'])
        self.assertTrue(average_fpl_value[3]['min'] <= eligibility['medicaid']['estimated_value'] <= average_fpl_value[3]['max'])