# Generated by Django 4.0.5 on 2023-05-09 20:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "programs",
            "0036_rename_has_2_person_federalpoverylimit_has_2_people_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="federalpoverylimit",
            name="year",
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
