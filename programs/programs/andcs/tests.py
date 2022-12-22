from django.test import TestCase
from programs.programs.andcs.andcs import Andcs
from screener.models import Screen, HouseholdMember, IncomeStream


class TestAndcs(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=2,
            household_assets=0,
            has_tanf=False,
            has_ssi=True
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
            relationship='spouse',
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

    def test_screen_exits(self):
        self.assertEqual(self.screen1.agree_to_tos, True)
        self.assertEqual(self.person1.screen, self.screen1)
        self.assertEqual(self.person2.screen, self.screen1)

    def test_andcs_visualy_impaired_is_eligible(self):
        self.person1.visually_impaired = True
        self.person1.save()
        andcs = Andcs(self.screen1)
        eligibility = andcs.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn(f"Must be receiving SSI", eligibility['passed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['passed'])
        self.assertIn(
            f"Household assets must not exceed {Andcs.asset_limit}", eligibility['passed'])
        self.assertIn(
            f"Someone in the household must have a disability or blindness", eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of {Andcs.min_age}-{Andcs.max_age}",
            eligibility['passed'])
        self.assertIn(
            f"A member of the household with a disability must make less than ${Andcs.grant_standard} a month",
            eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)

    def test_andcs_failed_all_conditions(self):
        self.screen1.has_ssi = False
        self.screen1.has_tanf = True
        self.screen1.household_assets = 2000
        self.screen1.save()
        andcs = Andcs(self.screen1)
        eligibility = andcs.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must be receiving SSI", eligibility['failed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['failed'])
        self.assertIn(
            f"Household assets must not exceed {Andcs.asset_limit}", eligibility['failed'])
        self.assertIn(
            f"Someone in the household must have a disability or blindness", eligibility['failed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of {Andcs.min_age}-{Andcs.max_age}",
            eligibility['failed'])
        self.assertIn(
            f"A member of the household with a disability must make less than ${Andcs.grant_standard} a month",
            eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)

    def test_andcs_failed_income_condition(self):
        self.person2.disabled = True
        self.person2.save()
        income = IncomeStream.objects.create(
            screen=self.screen1,
            household_member=self.person2,
            type='wages',
            amount=1748,
            frequency='monthly'
        )
        andcs = Andcs(self.screen1)
        eligibility = andcs.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must be receiving SSI", eligibility['passed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['passed'])
        self.assertIn(
            f"Household assets must not exceed {Andcs.asset_limit}", eligibility['passed'])
        self.assertIn(
            f"Someone in the household must have a disability or blindness", eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of {Andcs.min_age}-{Andcs.max_age}",
            eligibility['passed'])
        self.assertIn(
            f"A member of the household with a disability must make less than ${Andcs.grant_standard} a month",
            eligibility['failed'])

    def test_andcs_failed_age_condition(self):
        self.person2.disabled = True
        self.person2.visually_impaired = True
        self.person2.age = 60
        self.person2.save()
        andcs = Andcs(self.screen1)
        eligibility = andcs.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must be receiving SSI", eligibility['passed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['passed'])
        self.assertIn(
            f"Household assets must not exceed {Andcs.asset_limit}", eligibility['passed'])
        self.assertIn(
            f"Someone in the household must have a disability or blindness", eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of {Andcs.min_age}-{Andcs.max_age}",
            eligibility['failed'])
        self.assertIn(
            f"A member of the household with a disability must make less than ${Andcs.grant_standard} a month",
            eligibility['failed'])
