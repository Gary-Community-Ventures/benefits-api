# Generated by Django 4.2.15 on 2024-11-20 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("screener", "0088_alter_screen_white_label"),
    ]

    operations = [
        migrations.AddField(
            model_name="whitelabel",
            name="cms_method",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
