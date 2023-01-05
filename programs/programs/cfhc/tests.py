from django.test import TestCase
from programs.programs.cfhc.cfhc import Cfhc
from screener.models import Screen, HouseholdMember
from django.conf import settings


class TestCfhc(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=1,
            household_assets=0,
            has_employer_hi=True,
            has_private_hi=True,
            has_medicaid_hi=True,
            has_chp_hi=True,
            has_no_hi=True,
        )
        self.person1 = HouseholdMember.objects.create(
            screen=self.screen1,
            relationship='headOfHousehold',
            age=60,
            student=False,
            student_full_time=False,
            pregnant=False,
            unemployed=False,
            worked_in_last_18_mos=True,
            visually_impaired=False,
            disabled=False,
            veteran=False,
            has_income=False,
            has_expenses=False,
        )

    def test_health_insurance_pass_all_conditions(self):
        cfhc = Cfhc(self.screen1)
        eligibility = cfhc.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn(
            "Someone in the household must not have health insurance", eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)

    def test_health_insurance_failed_all_conditions(self):
        self.screen1.has_no_hi = False
        self.screen1.save()

        cfhc = Cfhc(self.screen1)
        eligibility = cfhc.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(
            "Someone in the household must not have health insurance", eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)
