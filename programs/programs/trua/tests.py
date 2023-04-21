from django.test import TestCase
from programs.programs.trua.calculator import Trua
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

    def test_trua_passed_all_conditions(self):
        trua = Trua(self.screen1)
        eligibility = trua.eligibility

        self.assertTrue(eligibility["eligible"])

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
