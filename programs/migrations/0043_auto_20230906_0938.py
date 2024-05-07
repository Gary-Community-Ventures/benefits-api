# Generated by Django 4.0.5 on 2023-09-06 15:38

from django.db import migrations


def connect_translations(apps, schema_editor):
    Program = apps.get_model("programs", "Program")
    Translation = apps.get_model("translations", "Translation")

    translated_fields = (
        "description_short",
        "name",
        "description",
        "learn_more_link",
        "apply_button_link",
        "value_type",
        "estimated_delivery_time",
        "estimated_application_time",
        "category",
    )
    for program in Program.objects.all():
        for field in translated_fields:
            translation = Translation.objects.get(
                label=f"program.{program.name_abbreviated}_{program.id}-{field}"
            )
            setattr(program, field + "_1", translation)
        program.save()


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0042_auto_20230905_1620"),
        ("translations", "0003_alter_translation_managers"),
    ]

    operations = [migrations.RunPython(connect_translations)]
