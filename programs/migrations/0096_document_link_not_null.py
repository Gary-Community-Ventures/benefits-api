# Generated by Django 4.2.15 on 2024-11-05 20:48
import uuid
from django.db import migrations, models
import django.db.models.deletion


def add_document_links(apps, schema_editor):
    Document = apps.get_model("programs", "Document")
    Translation = apps.get_model("translations", "Translation")

    for document in Document.objects.all():
        translation_link_url = Translation.objects.add_translation(
            f"document.{document.external_name or uuid.uuid4()}-{document.id}_link_url",
            "[PLACEHOLDER]",
        )
        translation_link_text = Translation.objects.add_translation(
            f"document.{document.external_name or uuid.uuid4()}-{document.id}_link_text",
            "[PLACEHOLDER]",
        )
        Document.objects.filter(pk=document.id).update(
            link_url=translation_link_url.id, link_text=translation_link_text.id
        )


class Migration(migrations.Migration):

    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0095_document_link"),
    ]

    operations = [
        migrations.RunPython(add_document_links, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="document",
            name="link_text",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="document_link_text",
                to="translations.translation",
            ),
        ),
        migrations.AlterField(
            model_name="document",
            name="link_url",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="document_link_url",
                to="translations.translation",
            ),
        ),
    ]
