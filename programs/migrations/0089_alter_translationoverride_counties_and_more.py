# Generated by Django 4.2.14 on 2024-09-30 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0088_translationoverride"),
    ]

    operations = [
        migrations.AlterField(
            model_name="translationoverride",
            name="counties",
            field=models.ManyToManyField(blank=True, related_name="translation_overrides", to="programs.county"),
        ),
        migrations.AlterField(
            model_name="translationoverride",
            name="program",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translation_overrides",
                to="programs.program",
            ),
        ),
    ]
