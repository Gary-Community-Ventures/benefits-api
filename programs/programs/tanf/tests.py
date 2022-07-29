from programs.programs.tanf.tanf import calculate_tanf
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household

class TANFTestCase(TestCase):
    def test_tanf_single_parent_two_children(self):
        screen = create_single_parent_two_children_household(annual_income=15000)
        calculation = calculate_tanf(screen)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 6096)