from typing import Any
from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFields, TranslatableManager
from django.conf import settings
from tqdm import trange
from dataclasses import dataclass
from integrations.util.cache import Cache
from translations.model_data import ModelDataController


BLANK_TRANSLATION_PLACEHOLDER = "[PLACEHOLDER]"


class TranslationCache(Cache):
    expire_time = 24 * 60 * 60
    default = {}

    def update(self):
        langs = [lang["code"] for lang in settings.PARLER_LANGUAGES[None]]
        translations = Translation.objects.prefetch_related("translations")
        translations_dict = {}
        for lang in langs:
            lang_translations = {}
            for translation in translations:
                if translation.active:
                    translation.set_current_language(lang)
                    lang_translations[translation.label] = translation.text
            translations_dict[lang] = lang_translations
        return translations_dict


class TranslationManager(TranslatableManager):
    use_in_migrations = True
    translation_cache = TranslationCache()

    def add_translation(self, label, default_message=BLANK_TRANSLATION_PLACEHOLDER, active=True, no_auto=False):
        default_lang = settings.LANGUAGE_CODE
        parent = self.get_or_create(label=label, defaults={"active": active, "no_auto": no_auto})[0]
        if parent.active != active or parent.active != no_auto:
            parent.active = active
            parent.no_auto = no_auto
            parent.save()

        parent.create_translation(default_lang, text=default_message, edited=True)
        self.translation_cache.invalid = True
        return parent

    def edit_translation(self, label, lang, translation, manual=True):
        parent = self.language(lang).get(label=label)

        if manual is False and parent.no_auto:
            return parent

        parent.text = translation
        parent.edited = manual
        parent.save()
        self.translation_cache.invalid = True
        return parent

    def edit_translation_by_id(self, id, lang, translation, manual=True):
        parent = self.prefetch_related("translations").language(lang).get(pk=id)

        if manual is False and parent.no_auto:
            return parent

        parent.text = translation
        parent.edited = manual
        parent.save()
        self.translation_cache.invalid = True
        return parent

    def all_translations(self, langs=[lang["code"] for lang in settings.PARLER_LANGUAGES[None]]):
        translations_dict = {}
        for lang in langs:
            translations_dict[lang] = self.translation_cache.fetch()[lang]

        return translations_dict

    def export_translations(self):
        all_langs = settings.PARLER_LANGUAGES[None]
        translations = self.prefetch_related("translations")

        translations_export = {"translations": {}, "model_data": {}}
        for i in trange(len(translations), desc="Translations"):
            translation = translations[i]
            related_instances = translation.get_reverse_instances()

            for relationship in related_instances:
                instance = relationship.instance

                if instance.external_name is None:
                    continue

                field_name = relationship.field_name
                TranslationExportBuilder: type[ModelDataController] = getattr(
                    instance, "TranslationExportBuilder", ModelDataController
                )

                export_builder = TranslationExportBuilder(instance)

                model_data = translations_export["model_data"]
                model_name = export_builder.model_name
                if model_name not in model_data:
                    model_data[model_name] = {
                        "meta_data": {"dependencies": TranslationExportBuilder.dependencies, "name": model_name},
                        "instance_data": {},
                    }
                instance_data = model_data[model_name]["instance_data"]

                if export_builder.external_name not in instance_data:
                    instance_data[export_builder.external_name] = {
                        "data": export_builder.to_model_data(),
                        "labels": {},
                        "external_name": export_builder.external_name,
                    }

                instance_data[export_builder.external_name]["labels"][field_name] = translation.label

            translations_export["translations"][translation.label] = {
                "langs": {},
                "no_auto": translation.no_auto,
                "active": translation.active,
            }

            for lang in all_langs:
                translation.set_current_language(lang["code"])
                translations_export["translations"][translation.label]["langs"][lang["code"]] = (
                    translation.text,
                    translation.edited,
                )

        return translations_export


class Translation(TranslatableModel):
    translations = TranslatedFields(
        text=models.TextField(null=True, blank=True), edited=models.BooleanField(default=False, null=False)
    )
    active = models.BooleanField(default=True, null=False)
    no_auto = models.BooleanField(default=False, null=False)
    label = models.CharField(max_length=128, null=False, blank=False, unique=True)

    objects = TranslationManager()

    def _get_reverses(self):
        """
        This method checks if the current Translation object is referenced by any related models
        such as Program, Navigator, UrgentNeed, or Document. It iterates through all reverse
        relationships of the Translation model and determines if any related object exists.
        It returns all of teh reverse relationships
        """

        relationships = []

        # determine if a translation is refrenced by either a program, navigator, urgent_need, or document
        # https://stackoverflow.com/questions/54711671/django-how-to-determine-if-an-object-is-referenced-by-any-other-object
        for reverse in (f for f in self._meta.get_fields() if f.auto_created and not f.concrete):
            if reverse.related_name == "translations":
                continue

            name = reverse.get_accessor_name()

            reverse_count = getattr(self, name).count()
            if reverse_count > 0:
                relationships.append(reverse)

        return relationships

    @dataclass
    class ReverseInstance:
        instance: Any
        field_name: Any

    def get_reverse_instances(self) -> list[ReverseInstance]:
        """
        Get list of instances and their relationship name that refrence this translation
        """
        reverses = self._get_reverses()

        instances: list[self.ReverseInstance] = []
        for reverse in reverses:
            name = reverse.get_accessor_name()
            instances.extend([self.ReverseInstance(instance, name) for instance in getattr(self, name).all()])

        return instances

    @property
    def used_by(self):
        """
        This property field stores information about the first model instance that uses
        this Translation object. It checks for related models and, if a relationship
        is found, retrieves the instance's ID, model name, field name, and display name (either
        an external name or an abbreviated name). If no relationship is found, it returns
        default values indicating the translation is unassigned.
        """
        reverses = self._get_reverses()
        if len(reverses) >= 1:
            reverse = reverses[0]
            instance = getattr(self, reverse.get_accessor_name()).first()
            model_name = reverse.related_model._meta.model_name
            field_name = reverse.field.name
            external_name = getattr(instance, "external_name", None)
            abbreviated_name = getattr(instance, "abbreviated_name", None)
            display_name = external_name if external_name else abbreviated_name
            return {"id": instance.id, "model_name": model_name, "field_name": field_name, "display_name": display_name}
        return {"id": None, "model_name": "unassigned", "field_name": None, "display_name": None}

    def get_lang(self, lang):
        return self.translations.filter(language_code=lang).first()

    @property
    def default_message(self):
        return self.get_lang(settings.LANGUAGE_CODE).text

    def __str__(self):
        return self.label
