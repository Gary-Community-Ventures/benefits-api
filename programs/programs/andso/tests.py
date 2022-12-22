from django.test import TestCase
from programs.programs.andso.andso import Andso
from screener.models import Screen, HouseholdMember, IncomeStream


class TestAndso(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=2,
            household_assets=0,
            has_tanf=False,
            has_ssi=False
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

    def test_andso_visualy_impaired_is_eligible(self):
        self.person1.visually_impaired=True
        self.person1.save()
        andso = Andso(self.screen1)
        eligibility = andso.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn(f"Must not be receiving SSI", eligibility['passed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['passed'])
        self.assertIn(f"Household assets must not exceed {Andso.asset_limit}", eligibility['passed'])
        self.assertIn(f"Someone in the household must have a disability or blindness", eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of 18-{Andso.max_age} (0-{Andso.max_age} for blindness)", 
            eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must have a total countable income less than ${Andso.grant_standard} a month",
            eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)

    def test_andso_failed_all_conditions(self):
        self.screen1.has_ssi = True
        self.screen1.has_tanf = True
        self.screen1.household_assets = 2000
        self.screen1.save()
        andso = Andso(self.screen1)
        eligibility = andso.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must not be receiving SSI", eligibility['failed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['failed'])
        self.assertIn(f"Household assets must not exceed {Andso.asset_limit}", eligibility['failed'])
        self.assertIn(f"Someone in the household must have a disability or blindness", eligibility['failed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of 18-{Andso.max_age} (0-{Andso.max_age} for blindness)",
            eligibility['failed'])
        self.assertIn(
            f"A member of the house hold with a disability must have a total countable income less than ${Andso.grant_standard} a month",
            eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)

    def test_andso_failed_income_condition(self):
        self.person2.disabled = True
        self.person2.save()
        income = IncomeStream.objects.create(
            screen=self.screen1,
            household_member=self.person2,
            type='wages',
            amount=562,
            frequency='monthly'
        )
        andso = Andso(self.screen1)
        eligibility = andso.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must not be receiving SSI", eligibility['passed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['passed'])
        self.assertIn(f"Household assets must not exceed {Andso.asset_limit}", eligibility['passed'])
        self.assertIn(f"Someone in the household must have a disability or blindness", eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of 18-{Andso.max_age} (0-{Andso.max_age} for blindness)",
            eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must have a total countable income less than ${Andso.grant_standard} a month",
            eligibility['failed'])

    def test_andso_failed_age_condition(self):
        self.person2.disabled = True
        self.person2.visually_impaired = True
        self.person2.age = 60
        self.person2.save()
        andso = Andso(self.screen1)
        eligibility = andso.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Must not be receiving SSI", eligibility['passed'])
        self.assertIn(f"Must not be eligible for TANF", eligibility['passed'])
        self.assertIn(
            f"Household assets must not exceed {Andso.asset_limit}", eligibility['passed'])
        self.assertIn(
            f"Someone in the household must have a disability or blindness", eligibility['passed'])
        self.assertIn(
            f"A member of the house hold with a disability must be between the ages of 18-{Andso.max_age} (0-{Andso.max_age} for blindness)",
            eligibility['failed'])
        self.assertIn(
            f"A member of the house hold with a disability must have a total countable income less than ${Andso.grant_standard} a month",
            eligibility['failed'])
