# Generated by Django 4.0.5 on 2023-05-08 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0061_alter_screen_is_test_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screen',
            name='is_test_data',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
