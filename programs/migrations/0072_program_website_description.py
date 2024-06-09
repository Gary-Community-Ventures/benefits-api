# Generated by Django 4.2.11 on 2024-05-21 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0071_alter_program_estimated_value"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="website_description",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="program_website_description",
                to="translations.translation",
            ),
        ),
    ]
