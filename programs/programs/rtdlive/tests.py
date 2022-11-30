from programs.programs.rtdlive.rtdlive import calculate_rtdlive
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household


class RTDLiveTestCase(TestCase):
    def test_rtdlive_single_parent_two_children(self):
        screen = create_single_parent_two_children_household(
            annual_income=15000)
        data = []
        calculation = calculate_rtdlive(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertEqual(calculation['value'], 750)
