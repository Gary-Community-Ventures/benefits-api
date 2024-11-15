# Generated by Django 4.2.15 on 2024-11-07 17:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0094_rename_category_v2_program_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="apply_button_description",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="program_apply_button_description",
                to="translations.translation",
            ),
        ),
    ]
