# Generated by Django 4.0.5 on 2022-10-18 14:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0015_programtranslation_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programtranslation",
            name="active",
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
