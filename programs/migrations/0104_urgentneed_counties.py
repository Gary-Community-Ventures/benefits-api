# Generated by Django 4.2.15 on 2025-03-13 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0103_urgentneed_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="urgentneed",
            name="counties",
            field=models.ManyToManyField(blank=True, related_name="urgent_need", to="programs.county"),
        ),
    ]
