from programs.programs.cccap.cccap import calculate_cccap
from django.test import TestCase
from screener.tests import create_single_parent_two_children_household
from django.conf import settings


class CCCAPTestCase(TestCase):
    def test_cccap_single_parent_two_children(self):
        expected_fpl_value = {
            3: {
                'min': 16000,
                'max': 18000
            }
        }

        fpl_limit = 2 * settings.FPL[3]
        screen = create_single_parent_two_children_household(
            annual_income=fpl_limit)
        data = []
        calculation = calculate_cccap(screen, data)
        self.assertTrue(calculation['eligibility']['eligible'])
        self.assertTrue(expected_fpl_value[3]['min'] <= calculation['value'] <= expected_fpl_value[3]['max'])
