# Generated by Django 4.2.15 on 2025-03-19 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "screener",
            "0101_screen_has_ccfa_screen_has_csfp_screen_has_ma_eaedc_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="insurance",
            name="mass_health",
            field=models.BooleanField(default=False),
        ),
    ]
