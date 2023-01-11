from django.test import TestCase
from programs.programs.cdhcs.cdhcs import Cdhcs
from screener.models import Screen, HouseholdMember, IncomeStream
from django.conf import settings


class TestCdhcsPension(TestCase):
    def setUp(self):
        self.screen1 = Screen.objects.create(
            agree_to_tos=True,
            zipcode='80205',
            county='Denver County',
            household_size=1,
            household_assets=0,
            has_no_hi=True
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

    def test_cdhcs_pass_all_conditions(self):
        cdhcs = Cdhcs(self.screen1)
        eligibility = cdhcs.eligibility

        self.assertTrue(eligibility["eligible"])

    def test_cdhcs_failed_all_conditions(self):
        self.person1.age = 20
        self.person1.save()
        IncomeStream.objects.create(
            screen=self.screen1,
            household_member=self.person1,
            type='wages',
            amount=3000,
            frequency='monthly'
        )

        cdhcs = Cdhcs(self.screen1)
        eligibility = cdhcs.eligibility

        self.assertFalse(eligibility["eligible"])
