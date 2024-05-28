# Generated by Django 4.0.5 on 2023-08-03 16:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("screener", "0063_alter_webhooktranslation_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="screen",
            name="needs_dental_care_help",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="screen",
            name="needs_job_resources",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name="screen",
            name="needs_legal_services",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
