# Generated by Django 4.0.5 on 2023-09-28 17:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0058_program_legal_status_required"),
    ]

    operations = [
        migrations.AlterField(
            model_name="program",
            name="legal_status_required",
            field=models.ManyToManyField(
                blank=True, related_name="programs", to="programs.legalstatus"
            ),
        ),
    ]
