# Generated by Django 4.2.15 on 2024-10-01 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("screener", "0084_screen_has_fatc"),
    ]

    operations = [
        migrations.AddField(
            model_name="householdmember",
            name="birth_year_month",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="householdmember",
            name="age",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
