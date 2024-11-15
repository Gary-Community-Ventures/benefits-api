# Generated by Django 4.2.15 on 2024-10-28 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("integrations", "0001_initial"),
        ("integrations", "0002_alter_link_hash"),
        ("integrations", "0003_alter_link_hash"),
        ("integrations", "0004_alter_link_link"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Link",
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
                ("link", models.URLField(max_length=2048, unique=True)),
                ("validated", models.BooleanField(default=False)),
                (
                    "hash",
                    models.CharField(blank=True, default=None, max_length=2048, null=True),
                ),
            ],
        ),
    ]