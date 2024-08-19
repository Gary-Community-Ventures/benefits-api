# Generated by Django 4.2.14 on 2024-08-19 18:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0081_merge_20240802_1619"),
    ]

    operations = [
        migrations.CreateModel(
            name="WarningMessage",
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
                (
                    "external_name",
                    models.CharField(
                        blank=True, max_length=120, null=True, unique=True
                    ),
                ),
                ("calculator", models.CharField(max_length=120)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="warning_message",
                        to="translations.translation",
                    ),
                ),
                (
                    "program",
                    models.ManyToManyField(
                        blank=True,
                        related_name="warning_message",
                        to="programs.program",
                    ),
                ),
            ],
        ),
    ]