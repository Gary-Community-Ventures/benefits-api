# Generated by Django 4.2.14 on 2024-08-19 19:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("translations", "0004_translation_no_auto"),
        ("programs", "0083_rename_navigatorcounty_county_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="warningmessage",
            name="counties",
            field=models.ManyToManyField(blank=True, related_name="warning_messages", to="programs.county"),
        ),
        migrations.AlterField(
            model_name="warningmessage",
            name="message",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="warning_messages",
                to="translations.translation",
            ),
        ),
        migrations.AlterField(
            model_name="warningmessage",
            name="program",
            field=models.ManyToManyField(blank=True, related_name="warning_messages", to="programs.program"),
        ),
    ]
