from translations.model_data import ModelDataController
from .models import Translation
from programs.models import Program, Navigator, UrgentNeed, Document, WarningMessage
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from tqdm import trange
from decouple import config


TRANSLATED_MODEL_MAP = {
    "Program": Program,
    "UrgentNeed": UrgentNeed,
    "Navigator": Navigator,
    "Document": Document,
    "WarningMessage": WarningMessage,
}

TRANSLATED_MODELS = TRANSLATED_MODEL_MAP.values()


@transaction.atomic
def bulk_add(translations):
    if config("ALLOW_TRANSLATION_IMPORT", "False") != "True":
        raise Exception("Translation import not allowed")

    for Model in TRANSLATED_MODELS:
        Model.objects.select_for_update().all()
    Translation.objects.select_for_update().all()

    order = model_order(translations["model_data"])

    TRANSLATION_PROGRESS_BAR_DESC = "Translations"
    longest_name = len(TRANSLATION_PROGRESS_BAR_DESC)
    for model_name in order:
        if len(model_name) > longest_name:
            longest_name = len(model_name)

    for model_name in order:
        Model = TRANSLATED_MODEL_MAP[model_name]
        TranslationExportBuilder: type[ModelDataController] = Model.TranslationExportBuilder

        model_data = list(translations["model_data"][model_name]["instance_data"].values())
        for i in trange(len(model_data), desc=model_name.ljust(longest_name, " ")):
            instance_data = model_data[i]
            instance = TranslationExportBuilder.initialize_instance(instance_data["external_name"], Model)
            builder = TranslationExportBuilder(instance)

            builder.from_model_data(instance_data["data"])

            for field, label in instance_data["labels"].items():
                translation = create_translation(label, translations["translations"][label])
                getattr(translation, field).set([instance])

    protected_translation_ids = []

    for Model in TRANSLATED_MODELS:
        protected_translation_ids += translation_ids(Model)

    Translation.objects.exclude(id__in=protected_translation_ids).delete()

    translations_data = list(translations["translations"].items())
    for i in trange(len(translations_data), desc=TRANSLATION_PROGRESS_BAR_DESC.ljust(longest_name, " ")):
        label, details = translations_data[i]
        create_translation(label, details)


def translation_ids(model):
    ids = []
    for obj in model.objects.all():
        for field in model.objects.translated_fields:
            ids.append(getattr(obj, field).id)

    return ids


def create_translation(label: str, details):
    translation = Translation.objects.add_translation(
        label, details["langs"][settings.LANGUAGE_CODE][0], active=details["active"], no_auto=details["no_auto"]
    )

    for lang, message in details["langs"].items():
        if lang == settings.LANGUAGE_CODE:
            continue
        Translation.objects.edit_translation_by_id(translation.id, lang, message[0], manual=message[1])

    return translation


def model_order(model_data):
    graph = {}
    for model in model_data.values():
        graph[model["meta_data"]["name"]] = model["meta_data"]["dependencies"]

    for node in graph:
        check_cycle(graph, [node])

    order = []

    for name in graph:
        add_model_to_order(order, graph, name)

    return order


def check_cycle(graph: dict[str, list[str]], visited: list[str]):
    for dependency in graph[visited[-1]]:
        if dependency not in graph:
            raise KeyError(f'"{dependency}" in "{visited[-1]}" is not a valid depenendency')
        if dependency in visited:
            # if the dependency is in visited, that means that there is a cycle
            raise Exception("circular dependencies detected")

        check_cycle(graph, [*visited, dependency])


def add_model_to_order(order: list[str], graph: dict[str, list[str]], name: str):
    if name in order:
        return

    for dependency in graph[name]:
        # dependencies should be added to the list first
        add_model_to_order(order, graph, dependency)

    order.append(name)
