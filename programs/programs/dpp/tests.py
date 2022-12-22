from django.test import TestCase
from programs.programs.dpp.dpp import Dpp
from screener.models import Screen, HouseholdMember


class TestDpp(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=2
        )
        self.person1 = HouseholdMember.objects.create(
            screen=self.screen1,
            relationship='headOfHousehold',
            age=30,
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
            age=3,
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

    def test_screen_exits(self):
        self.assertEqual(self.screen1.agree_to_tos, True)
        self.assertEqual(self.person1.screen, self.screen1)
        self.assertEqual(self.person2.screen, self.screen1)

    def test_dpp_has_preschooler(self):
        dpp = Dpp(self.screen1)
        eligibility = dpp.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn(f"Must have a child between the ages of {Dpp.min_age} and {Dpp.max_age}", eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)
    
    def test_dpp_doesnt_have_preschooler(self):
        self.person2.age = 5
        self.person2.save()
        dpp = Dpp(self.screen1)
        eligibility = dpp.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must have a child between the ages of {Dpp.min_age} and {Dpp.max_age}", eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)
