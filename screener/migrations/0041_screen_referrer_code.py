# Generated by Django 4.0.5 on 2023-01-25 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0040_screen_has_chp_hi_screen_has_employer_hi_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='screen',
            name='referrer_code',
            field=models.CharField(blank=True, default=None, max_length=320, null=True),
        ),
    ]