# Generated by Django 4.2.6 on 2024-01-22 21:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("screener", "0077_rename_has_wap_screen_has_cowap"),
    ]

    operations = [
        migrations.AddField(
            model_name="screen",
            name="has_ubp",
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
