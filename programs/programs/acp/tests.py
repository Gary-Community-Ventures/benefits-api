from programs.programs.acp.acp import calculate_acp
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household


class ACPTestCase(TestCase):
    def test_acp_single_parent_two_children(self):
        screen = create_single_parent_two_children_household(
            annual_income=15000)
        data = []
        calculation = calculate_acp(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 360)
