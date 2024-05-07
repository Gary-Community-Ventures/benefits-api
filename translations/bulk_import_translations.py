from .models import Translation
from programs.models import Program, Navigator, UrgentNeed, Document
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from tqdm import trange
from decouple import config


@transaction.atomic
def bulk_add(translations):
    if config("ALLOW_TRANSLATION_IMPORT", "False") != "True":
        raise Exception("Translation import not allowed")

    protected_translation_ids = []
    Translation.objects.select_for_update().all()
    protected_translation_ids += translation_ids(Program)
    protected_translation_ids += translation_ids(Navigator)
    protected_translation_ids += translation_ids(UrgentNeed)
    protected_translation_ids += translation_ids(Document)

    Program.objects.select_for_update().all()
    UrgentNeed.objects.select_for_update().all()

    Program.objects.all().update(active=False)
    UrgentNeed.objects.all().update(active=False)

    Translation.objects.exclude(id__in=protected_translation_ids).delete()

    translations_data = list(translations.items())
    for i in trange(len(translations_data), desc="Translations"):
        label, details = translations_data[i]
        translation = Translation.objects.add_translation(
            label, details["langs"][settings.LANGUAGE_CODE][0], active=details["active"], no_auto=details["no_auto"]
        )
        del details["langs"][settings.LANGUAGE_CODE]

        if details["reference"] is not False:
            ref = details["reference"]
            if ref[0] == "programs_program":
                try:
                    obj = Program.objects.get(external_name=ref[1])
                    obj.active = True
                except ObjectDoesNotExist:
                    obj = Program.objects.new_program(ref[1])
                    obj.external_name = ref[1]
                obj.save()
            elif ref[0] == "programs_navigator":
                try:
                    obj = Navigator.objects.get(external_name=ref[1])
                except ObjectDoesNotExist:
                    obj = Navigator.objects.new_navigator(ref[1], None)
                    obj.external_name = ref[1]
                    obj.save()
            elif ref[0] == "programs_urgentneed":
                try:
                    obj = UrgentNeed.objects.get(external_name=ref[1])
                    obj.active = True
                except ObjectDoesNotExist:
                    obj = UrgentNeed.objects.new_urgent_need(ref[1], None)
                    obj.external_name = ref[1]
                obj.save()
            elif ref[0] == "programs_document":
                try:
                    obj = Document.objects.get(external_name=ref[1])
                except ObjectDoesNotExist:
                    obj = Document.objects.new_document(ref[1])

            getattr(translation, ref[2]).set([obj])

        for lang, message in details["langs"].items():
            Translation.objects.edit_translation_by_id(translation.id, lang, message[0], manual=message[1])


def translation_ids(model):
    ids = []
    for obj in model.objects.all():
        for field in model.objects.translated_fields:
            ids.append(getattr(obj, field).id)

    return ids
