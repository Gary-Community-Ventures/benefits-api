# Generated by Django 4.0.5 on 2023-03-02 21:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("screener", "0046_alter_screen_uuid"),
    ]

    operations = [
        migrations.AddField(
            model_name="incomestream",
            name="hours_worked",
            field=models.IntegerField(null=True),
        ),
    ]
