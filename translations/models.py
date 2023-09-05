from django.db import models
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from django.conf import settings


class TranslationManager(TranslatableManager):
    def add_translation(self, label, default_message):
        default_lang = settings.LANGUAGE_CODE
        parent = self.create(label=label, active=True)
        parent.create_translation(default_lang, text=default_message, edited=True)

    def edit_translation(self, label, lang, translation, manual=True):
        parent = self.language(lang).get(label=label)
        parent.text = translation
        parent.edited = manual
        parent.save()

    def all_translations(self):
        all_langs = settings.PARLER_LANGUAGES[None]
        translations = self.prefetch_related('translations')
        translations_dict = {}
        for lang in all_langs:
            lang_translations = {}
            for translation in translations:
                if translation.active:
                    translation.set_current_language(lang['code'])
                    lang_translations[translation.label] = translation.text
            translations_dict[lang['code']] = lang_translations
        return translations_dict

    def bulk_add(self, translations):
        for lang, translation in translations.items():
            for label, message in translation.items():
                text, edited = message
                if lang == settings.LANGUAGE_CODE:
                    self.add_translation(label, text)
                else:
                    self.edit_translation(label, lang, text, edited)


class Translation(TranslatableModel):
    translations = TranslatedFields(
        text=models.TextField(null=True, blank=True),
        edited=models.BooleanField(default=False, null=False)
    )
    active = models.BooleanField(default=True, null=False)
    label = models.CharField(max_length=128, null=False, blank=False, unique=True)

    objects = TranslationManager()

    def __str__(self):
        return self.label
