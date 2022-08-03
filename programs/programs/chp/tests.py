from programs.programs.chp.chp import calculate_chp
from programs.programs.policyengine.policyengine import eligibility_policy_engine
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household
from django.conf import settings

class CHPTestCase(TestCase):
    def test_chp_single_parent_two_children(self):
        # todo: why is MEDICAID returning eligible beyond the colorado household income table
        fpl_limit = 2 * settings.FPL[3]
        screen = create_single_parent_two_children_household(annual_income=fpl_limit)

        # CHP+ eligibility depends on MEDICAID eligibility
        data = []
        eligibility = eligibility_policy_engine(screen)
        data.append(
            {
                "short_name": "medicaid",
                "eligible": eligibility["medicaid"]["eligible"]
            })

        calculation = calculate_chp(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 400)