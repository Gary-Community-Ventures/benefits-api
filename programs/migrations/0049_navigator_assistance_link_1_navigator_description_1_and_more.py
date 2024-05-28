# Generated by Django 4.0.5 on 2023-09-06 20:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translations', '0003_alter_translation_managers'),
        ('programs', '0048_rename_active_1_program_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='navigator',
            name='assistance_link_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='navigator_assistance_link', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='navigator',
            name='description_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='navigator_name_description', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='navigator',
            name='email_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='navigator_email', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='navigator',
            name='name_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='navigator_name', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='urgentneed',
            name='description_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='urgent_need_description', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='urgentneed',
            name='link_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='urgent_need_link', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='urgentneed',
            name='name_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='urgent_need_name', to='translations.translation'),
        ),
        migrations.AddField(
            model_name='urgentneed',
            name='type_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='urgent_need_type', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='apply_button_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_apply_button_link', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_category', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_description', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='description_short',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_description_short', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='estimated_application_time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_estimated_application_time', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='estimated_delivery_time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_estimated_delivery_time', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='learn_more_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_learn_more_link', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_name', to='translations.translation'),
        ),
        migrations.AlterField(
            model_name='program',
            name='value_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='program_value_type', to='translations.translation'),
        ),
    ]
