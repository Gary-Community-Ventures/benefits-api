# Generated by Django 4.0.5 on 2022-08-13 21:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("screener", "0018_screen_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="screen",
            name="start_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
