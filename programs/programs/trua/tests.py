from django.test import TestCase
from programs.programs.trua.trua import Trua
from screener.models import Screen, HouseholdMember, IncomeStream


class TestTruaPension(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=1,
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

    def test_trua_visualy_impaired_is_eligible(self):
        trua = Trua(self.screen1)
        eligibility = trua.eligibility

        self.assertTrue(eligibility["eligible"])
        self.assertIn(f"Household makes $0 per month which must be less than ${int(Trua.income_bands[1]/12)}", eligibility['passed'])
        self.assertIn("Must live in Denver", eligibility['passed'])
        self.assertEqual(len(eligibility['failed']), 0)

    def test_trua_failed_all_conditions(self):
        income = IncomeStream.objects.create(
            screen=self.screen1,
            household_member=self.person1,
            type='wages',
            amount=5800,
            frequency='monthly'
        )
        self.screen1.county = ''
        self.screen1.save()

        trua = Trua(self.screen1)
        eligibility = trua.eligibility

        self.assertFalse(eligibility["eligible"])
        self.assertIn(f"Household makes $5800.00 per month which must be less than ${int(Trua.income_bands[1]/12)}", eligibility['failed'])
        self.assertIn("Must live in Denver", eligibility['failed'])
        self.assertEqual(len(eligibility['passed']), 0)
