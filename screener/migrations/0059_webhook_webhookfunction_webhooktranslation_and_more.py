# Generated by Django 4.0.5 on 2023-05-03 22:17

from django.db import migrations, models
import django.db.models.deletion
import parler.fields
import parler.models


class Migration(migrations.Migration):
    dependencies = [
        ("screener", "0058_webhookfunctions_webhooks_webhookstranslation"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebHook",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("referrer_code", models.CharField(max_length=120)),
                ("url", models.CharField(max_length=320)),
            ],
            options={
                "abstract": False,
            },
            bases=(parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="WebHookFunction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name="WebHookTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(db_index=True, max_length=15, verbose_name="Language")),
                ("consent_text", models.TextField()),
                (
                    "master",
                    parler.fields.TranslationsForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="screener.webhook",
                    ),
                ),
            ],
            options={
                "verbose_name": "web hook Translation",
                "db_table": "screener_webhook_translation",
                "db_tablespace": "",
                "managed": True,
                "default_permissions": (),
                "unique_together": {("language_code", "master")},
            },
            bases=(parler.models.TranslatedFieldsModelMixin, models.Model),
        ),
        migrations.DeleteModel(
            name="WebHookFunctions",
        ),
        migrations.AlterUniqueTogether(
            name="webhookstranslation",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="webhookstranslation",
            name="master",
        ),
        migrations.DeleteModel(
            name="WebHooks",
        ),
        migrations.DeleteModel(
            name="WebHooksTranslation",
        ),
        migrations.AddField(
            model_name="webhook",
            name="functions",
            field=models.ManyToManyField(related_name="function", to="screener.webhookfunction"),
        ),
    ]
