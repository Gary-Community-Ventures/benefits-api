# Generated by Django 4.2.15 on 2024-10-29 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("integrations", "0006_link_valid_status_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="link",
            name="in_use",
            field=models.BooleanField(default=False),
        ),
    ]
