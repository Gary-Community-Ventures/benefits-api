# Generated by Django 4.2.15 on 2025-03-06 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("screener", "0099_remove_energycalculatormember_disabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="screen",
            name="has_ncscca",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
