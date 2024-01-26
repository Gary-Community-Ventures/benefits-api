# Generated by Django 4.2.6 on 2024-01-22 17:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0062_document_program_documents"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="document",
            name="name",
        ),
        migrations.AddField(
            model_name="document",
            name="external_name",
            field=models.CharField(blank=True, max_length=120, null=True, unique=True),
        ),
    ]
