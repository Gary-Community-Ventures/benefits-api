from programs.programs.cocb.cocb import calculate_cocb
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household

class COCBTestCase(TestCase):
    def test_cocb_single_parent_two_children(self):
        screen = create_single_parent_two_children_household(annual_income=15000)
        data = []
        calculation = calculate_cocb(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 750)