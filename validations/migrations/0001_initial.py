# Generated by Django 4.2.14 on 2024-07-24 20:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("screener", "0084_screen_has_fatc"),
    ]

    operations = [
        migrations.CreateModel(
            name="Validation",
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
                ("program_name", models.CharField(max_length=120)),
                ("eligible", models.BooleanField()),
                ("value", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_date", models.DateTimeField(auto_now=True)),
                (
                    "screen",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="validations",
                        to="screener.screen",
                    ),
                ),
            ],
        ),
    ]
