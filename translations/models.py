from django.db import models
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from django.conf import settings


class TranslationManager(TranslatableManager):
    use_in_migrations = True

    def add_translation(self, label, default_message, active=True, no_auto=False):
        default_lang = settings.LANGUAGE_CODE
        parent = self.get_or_create(label=label, defaults={
                                    'active': active, 'no_auto': no_auto})[0]
        if parent.active != active or parent.active != no_auto:
            parent.active = active
            parent.no_auto = no_auto
            parent.save()

        parent.create_translation(
            default_lang, text=default_message, edited=True)
        return parent

    def edit_translation(self, label, lang, translation, manual=True):
        parent = self.language(lang).get(label=label)

        if manual is False and parent.no_auto:
            return parent

        parent.text = translation
        parent.edited = manual
        parent.save()
        return parent

    def edit_translation_by_id(self, id, lang, translation, manual=True):
        parent = self.prefetch_related(
            'translations').language(lang).get(pk=id)

        if manual is False and parent.no_auto:
            return parent

        parent.text = translation
        parent.edited = manual
        parent.save()
        return parent

    def all_translations(self, langs=[lang['code'] for lang in settings.PARLER_LANGUAGES[None]]):
        translations = self.prefetch_related('translations')
        translations_dict = {}
        for lang in langs:
            lang_translations = {}
            for translation in translations:
                if translation.active:
                    translation.set_current_language(lang)
                    lang_translations[translation.label] = translation.text
            translations_dict[lang] = lang_translations
        return translations_dict

    def export_translations(self):
        all_langs = settings.PARLER_LANGUAGES[None]
        translations = self.prefetch_related('translations')

        translations_export = {}
        for translation in translations:
            reference = translation.in_program()

            if reference is True:
                continue

            translations_export[translation.label] = {
                'active': translation.active,
                'no_auto': translation.no_auto,
                'langs': {},
                'reference': reference,
            }

            for lang in all_langs:
                translation.set_current_language(lang['code'])
                translations_export[translation.label]['langs'][lang['code']] = (
                    translation.text, translation.edited)

        return translations_export


class Translation(TranslatableModel):
    translations = TranslatedFields(
        text=models.TextField(null=True, blank=True),
        edited=models.BooleanField(default=False, null=False)
    )
    active = models.BooleanField(default=True, null=False)
    no_auto = models.BooleanField(default=False, null=False)
    label = models.CharField(max_length=128, null=False,
                             blank=False, unique=True)

    objects = TranslationManager()

    def find_used_model(self, label_unpack=False):
        has_relationship = False
        # determine if a translation is refrenced by either a program, navigator, urgent_need, or document
        # https://stackoverflow.com/questions/54711671/django-how-to-determine-if-an-object-is-referenced-by-any-other-object
        for reverse in (f for f in self._meta.get_fields() if f.auto_created and not f.concrete):
            if reverse.related_name == 'translations':
                continue
            name = reverse.get_accessor_name()
            has_reverse_other = getattr(self, name).count()
            if has_reverse_other:
                if label_unpack:
                    return reverse.related_model._meta.model_name
                try:
                    active = getattr(self, reverse.related_name).first().active
                except AttributeError:
                    active = True

                external_name = getattr(
                    self, reverse.related_name).first().external_name
                table = getattr(
                    self, reverse.related_name).first()._meta.db_table
                if external_name:
                    return (table, external_name, reverse.related_name, active)
                has_relationship = True

        return has_relationship

    @ property
    def used_by(self):
        model_name = self.find_used_model(label_unpack=True)

        if not model_name:
            return 'unassigned'

        return model_name

    def get_lang(self, lang):
        return self.translations.filter(language_code=lang).first()

    def in_program(self):
        has_relationship = self.find_used_model()
        return has_relationship

    def __str__(self):
        return self.label
