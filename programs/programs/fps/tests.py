from django.test import TestCase
from programs.programs.fps.fps import Fps
from screener.models import Screen, HouseholdMember, IncomeStream
from django.conf import settings


class TestFpsPension(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=2,
            household_assets=0,
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
        self.person2 = HouseholdMember.objects.create(
            screen=self.screen1,
            relationship='child',
            age=10,
            student=True,
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

    def test_fps_pass_all_conditions(self):
        fps = Fps(self.screen1, [{"name_abbreviated": 'medicaid', "eligible": False}])
        eligibility = fps.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn(
            "Must not be eligible for Medicaid", eligibility['passed'])
        self.assertIn(
            f"Must have a child under the age of {Fps.child_max_age} or have someone who is pregnant",
            eligibility['passed'])
        self.assertIn(
            f"Income of $0 must be less than ${int(2.6 * settings.FPL2022[2]/12)}",
            eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)

    def test_fps_failed_all_conditions(self):
        self.person2.age = 20
        self.person2.save()
        IncomeStream.objects.create(
            screen=self.screen1,
            household_member=self.person1,
            type='wages',
            amount=4000,
            frequency='monthly'
        )

        fps = Fps(self.screen1, 
                [{"name_abbreviated": 'medicaid', "eligible": True}])
        eligibility = fps.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(
            "Must not be eligible for Medicaid", eligibility['failed'])
        self.assertIn(
            f"Must have a child under the age of {Fps.child_max_age} or have someone who is pregnant",
            eligibility['failed'])
        self.assertIn(
            f"Income of $4000 must be less than ${int(2.6 * settings.FPL2022[2]/12)}",
            eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)
