from django.test import TestCase
from programs.programs.cpcr.cpcr import Cpcr
from screener.models import Screen, HouseholdMember, IncomeStream


class TestCpcrPension(TestCase):
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
            age=65,
            student=False,
            student_full_time=False,
            pregnant=False,
            unemployed=False,
            worked_in_last_18_mos=True,
            visually_impaired=False,
            disabled=True,
            veteran=False,
            has_income=False,
            has_expenses=False,
        )

    def test_screen_exits(self):
        self.assertEqual(self.screen1.agree_to_tos, True)
        self.assertEqual(self.person1.screen, self.screen1)

    def test_cpcr_visualy_impaired_is_eligible(self):
        cpcr = Cpcr(self.screen1)
        eligibility = cpcr.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn("Someone in the household is disabled", eligibility['passed'])
        self.assertIn(f"Someone in your househould is over the age of {Cpcr.min_age}", eligibility['passed'])
        self.assertIn(f"Gross anual income must be less than {Cpcr.income_limit['single']}", eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)

    def test_cpcr_failed_all_conditions(self):
        self.person1.age = 30
        self.person1.disabled = False
        self.person1.save()
        income = IncomeStream.objects.create(
                    screen=self.screen1,
                    household_member=self.person1,
                    type='wages',
                    amount=2000,
                    frequency='monthly'
                )

        cpcr = Cpcr(self.screen1)
        eligibility = cpcr.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Someone in the household must be disabled or over the age of {Cpcr.min_age}", eligibility['failed'])
        self.assertIn(f"Gross anual income must be less than {Cpcr.income_limit['single']}", eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)
