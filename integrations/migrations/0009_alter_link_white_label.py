# Generated by Django 4.2.15 on 2024-11-05 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("screener", "0088_alter_screen_white_label"),
        ("integrations", "0008_link_white_label"),
    ]

    operations = [
        migrations.AlterField(
            model_name="link",
            name="white_label",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="links",
                to="screener.whitelabel",
            ),
        ),
    ]
