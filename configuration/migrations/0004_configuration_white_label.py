# Generated by Django 4.2.15 on 2024-11-05 20:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("screener", "0086_whitelabel_screen_white_label"),
        ("configuration", "0003_alter_configuration_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="configuration",
            name="white_label",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="configurations",
                to="screener.whitelabel",
            ),
        ),
    ]
