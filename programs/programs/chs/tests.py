from django.test import TestCase
from programs.programs.chs.chs import Chs
from screener.models import Screen, HouseholdMember, IncomeStream
from django.conf import settings


class TestChsPension(TestCase):
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
            age=4,
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

    def test_chs_visualy_impaired_is_eligible(self):
        chs = Chs(self.screen1)
        eligibility = chs.eligibility

        self.assertTrue(eligibility["eligible"])

    def test_chs_failed_all_conditions(self):
        income = IncomeStream.objects.create(
            screen=self.screen1,
            household_member=self.person1,
            type='wages',
            amount=2000,
            frequency='monthly'
        )
        self.screen1.save()
        self.person2.age=6
        self.person2.save()

        chs = Chs(self.screen1)
        eligibility = chs.eligibility

        self.assertFalse(eligibility["eligible"])