# Generated by Django 4.2.15 on 2025-05-20 22:15

from django.db import migrations


def add_warning_message_links(apps, schema_editor):
    WarningMessage = apps.get_model("programs", "WarningMessage")
    Translation = apps.get_model("translations", "Translation")

    for warning in WarningMessage.objects.all():
        translation_link_url = Translation.objects.add_translation(
            f"warning.{warning.calculator}-{warning.id}_link_url", "", no_auto=True
        )
        translation_link_text = Translation.objects.add_translation(
            f"warning.{warning.calculator}-{warning.id}_link_text",
            "",
        )
        WarningMessage.objects.filter(pk=warning.id).update(
            link_url=translation_link_url.id, link_text=translation_link_text.id
        )


class Migration(migrations.Migration):

    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0108_warningmessage_link_text_warningmessage_link_url"),
    ]

    operations = [
        migrations.RunPython(add_warning_message_links, migrations.RunPython.noop),
    ]
