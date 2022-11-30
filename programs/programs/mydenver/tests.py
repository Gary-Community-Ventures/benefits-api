from programs.programs.mydenver.mydenver import calculate_mydenver
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household


class MyDenverTestCase(TestCase):
    def test_mydenver_single_parent_two_children(self):
        screen = create_single_parent_two_children_household(
            annual_income=15000)
        data = []
        calculation = calculate_mydenver(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 300)
