from django.test import TestCase
from programs.programs.co.reproductive_health_care.calculator import ReproductiveHealthCare
from screener.models import Screen, HouseholdMember, WhiteLabel


class TestReproductiveHealthCarePension(TestCase):
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

    def test_reproductive_health_care_pass_all_conditions(self):
        rhc = ReproductiveHealthCare(self.screen1, [{"name_abbreviated": "medicaid", "eligible": True}])
        eligibility = rhc.eligibility

        self.assertTrue(eligibility["eligible"])

    def test_reproductive_health_care_failed_all_conditions(self):
        self.person1.has_no_hi = False
        self.person1.save()

        rhc = ReproductiveHealthCare(self.screen1, [{"name_abbreviated": "medicaid", "eligible": False}])
        eligibility = rhc.eligibility

        self.assertFalse(eligibility["eligible"])
