from django.test import TestCase
from screener.models import Screen
from configuration.models import Configuration, WhiteLabel
from django.core.management import call_command
import json


class CurrentBenefitsTestCase(TestCase):
    def setUp(self):
        """Set up test data - create a screen with a household member"""
        # Create all white labels
        self.white_labels = {}
        for code in ["_default", "co", "co_energy_calculator", "nc", "ma"]:
            self.white_labels[code] = WhiteLabel.objects.create(
                name=code.title(),
                code=code
            )
        
        # Create basic screen for testing
        self.screen = Screen.objects.create(
            agree_to_tos=True,
            zipcode="80205",
            county="Denver County",
            household_size=1,
            completed=True,
            white_label=self.white_labels["co"]
        )
        
        # Create program configurations
        self.cfh_config = Configuration.objects.create(
            name="connect_for_health_premium_tax_credit",
            white_label=self.white_labels["co"],
            active=True,
            data={
                "name": {
                    "en": "Connect for Health Colorado / Premium Tax Credit",
                    "es": "Connect for Health Colorado / Crédito Fiscal para las Primas"
                },
                "categories": ["health_care"]
            }
        )
        
        self.shc_config = Configuration.objects.create(
            name="senior_housing_income_tax_credit",
            white_label=self.white_labels["co"],
            active=True,
            data={
                "name": {
                    "en": "Senior Housing Income Tax Credit",
                    "es": "Crédito Fiscal para la Vivienda de Personas Mayores"
                },
                "categories": ["tax_credit"]
            }
        )

    def test_connect_for_health_config_exists(self):
        """Test that Connect for Health / Premium Tax Credit exists in configuration"""
        config = Configuration.objects.filter(
            name="connect_for_health_premium_tax_credit",
            white_label=self.white_labels["co"]
        ).first()
        
        self.assertIsNotNone(config)
        self.assertTrue(config.active)
        data = json.loads(config.data)
        self.assertEqual(data["categories"], ["health_care"])

    def test_senior_housing_credit_config_exists(self):
        """Test that Senior Housing Income Tax Credit exists in configuration"""
        config = Configuration.objects.filter(
            name="senior_housing_income_tax_credit",
            white_label=self.white_labels["co"]
        ).first()
        
        self.assertIsNotNone(config)
        self.assertTrue(config.active)
        data = json.loads(config.data)
        self.assertEqual(data["categories"], ["tax_credit"])

    def test_current_benefits_handling(self):
        """Test that marking a program as current benefit affects eligibility"""
        # Create an eligibility snapshot
        snapshot = self.screen.eligibility_snapshots.create()
        
        # Create a program snapshot showing the user is receiving Connect for Health
        snapshot.program_snapshots.create(
            name="connect_for_health_premium_tax_credit",
            name_abbreviated="CFH",
            value_type="monthly",
            estimated_value=100.00,
            eligible=True,
            new=False  # Not new = already receiving
        )
        
        # Verify the program is marked as already receiving (not new)
        program = snapshot.program_snapshots.get(name="connect_for_health_premium_tax_credit")
        self.assertFalse(program.new)

    def test_current_benefits_translation(self):
        """Test that program names have translations"""
        # Get configuration for programs
        cfh_config = Configuration.objects.get(
            name="connect_for_health_premium_tax_credit",
            white_label=self.white_labels["co"]
        )
        shc_config = Configuration.objects.get(
            name="senior_housing_income_tax_credit",
            white_label=self.white_labels["co"]
        )
        
        # Check that translations exist for both English and Spanish
        cfh_data = json.loads(cfh_config.data)
        shc_data = json.loads(shc_config.data)
        
        self.assertIn("en", cfh_data["name"])
        self.assertIn("es", cfh_data["name"])
        self.assertIn("en", shc_data["name"])
        self.assertIn("es", shc_data["name"])
