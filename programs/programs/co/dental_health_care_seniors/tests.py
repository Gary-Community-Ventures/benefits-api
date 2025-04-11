from django.test import TestCase
from programs.programs.co.dental_health_care_seniors.calculator import DentalHealthCareSeniors
from screener.models import Screen, HouseholdMember, IncomeStream, WhiteLabel


class TestDentalHealthCareSeniorsPension(TestCase):
    def setUp(self):
        # Create a WhiteLabel entry for tests
        self.white_label = WhiteLabel.objects.create(name="Test Label", code="test")
        
        self.screen1 = Screen.objects.create(
            white_label=self.white_label,
            completed=False,
            agree_to_tos=True,
            zipcode="80205",
            county="Denver County",
            household_size=1,
            household_assets=0,
            has_no_hi=True,
        )
        self.person1 = HouseholdMember.objects.create(
            screen=self.screen1,
            relationship="headOfHousehold",
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

    def test_dental_health_care_seniors_pass_all_conditions(self):
        cdhcs = DentalHealthCareSeniors(self.screen1)
        eligibility = cdhcs.eligibility

        self.assertTrue(eligibility["eligible"])

    def test_dental_health_care_seniors_failed_all_conditions(self):
        self.person1.age = 20
        self.person1.save()
        self.screen1.has_medicaid = True
        self.screen1.save()
        IncomeStream.objects.create(
            screen=self.screen1, household_member=self.person1, type="wages", amount=3000, frequency="monthly"
        )

        cdhcs = DentalHealthCareSeniors(self.screen1)
        eligibility = cdhcs.eligibility

        self.assertFalse(eligibility["eligible"])
