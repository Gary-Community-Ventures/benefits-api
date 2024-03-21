# Generated by Django 4.2.6 on 2024-03-21 14:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("configuration", "0002_alter_configuration_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="StateSpecificModifier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("state", models.CharField(max_length=2)),
                ("name", models.CharField(max_length=320)),
                ("data", models.JSONField(default=dict)),
            ],
        ),
    ]
