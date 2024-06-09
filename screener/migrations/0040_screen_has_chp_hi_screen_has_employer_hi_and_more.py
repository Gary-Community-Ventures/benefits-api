# Generated by Django 4.0.5 on 2023-01-03 23:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("screener", "0039_screen_has_ssi"),
    ]

    operations = [
        migrations.AddField(
            model_name="screen",
            name="has_chp_hi",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="screen",
            name="has_employer_hi",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="screen",
            name="has_medicaid_hi",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="screen",
            name="has_no_hi",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="screen",
            name="has_private_hi",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
