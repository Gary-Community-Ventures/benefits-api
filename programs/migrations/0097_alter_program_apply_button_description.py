# Generated by Django 4.2.15 on 2024-11-07 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0096_auto_20241107_1221"),
    ]

    operations = [
        migrations.AlterField(
            model_name="program",
            name="apply_button_description",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="program_apply_button_description",
                to="translations.translation",
            ),
        ),
    ]
