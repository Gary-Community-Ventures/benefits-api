# Generated by Django 4.0.5 on 2022-08-18 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screener', '0022_rename_messages_message'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='message',
            new_name='content',
        ),
        migrations.AddField(
            model_name='message',
            name='type',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
