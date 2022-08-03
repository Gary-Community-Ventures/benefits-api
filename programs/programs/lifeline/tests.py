from programs.programs.lifeline.lifeline import calculate_lifeline
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household

class ACPTestCase(TestCase):
    def test_lifeline_single_parent_two_children(self):
        screen = create_single_parent_two_children_household(annual_income=15000)
        data = []
        calculation = calculate_lifeline(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 111)