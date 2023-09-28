from .models import Translation
from programs.models import Program, Navigator, UrgentNeed
from django.db import transaction
from django.conf import settings
from decouple import config


@transaction.atomic
def bulk_add(translations):
    if config('ALLOW_TRANSLATION_IMPORT', 'False') != 'True':
        raise Exception('Translation import not allowed')

    protected_translation_ids = []
    Translation.objects.select_for_update().all()
    protected_translation_ids += translation_ids(Program)
    protected_translation_ids += translation_ids(Navigator)
    protected_translation_ids += translation_ids(UrgentNeed)

    Program.objects.select_for_update().all()
    UrgentNeed.objects.select_for_update().all()

    Program.objects.all().update(active=False)
    UrgentNeed.objects.all().update(active=False)

    Translation.objects.exclude(id__in=protected_translation_ids).delete()
    for label, details in translations.items():
        translation = Translation.objects.add_translation(
            label,
            details['langs'][settings.LANGUAGE_CODE][0],
            active=details['active']
        )
        del details['langs'][settings.LANGUAGE_CODE]

        if details['reference'] is not False:
            ref = details['reference']
            if ref[0] == 'programs_program':
                obj = Program.objects.get(external_name=details['reference'][1])
                obj.active = True
                obj.save()
            if ref[0] == 'programs_navigator':
                obj = Navigator.objects.get(external_name=details['reference'][1])
            if ref[0] == 'programs_urgentneed':
                obj = UrgentNeed.objects.get(external_name=details['reference'][1])
                obj.active = True
                obj.save()
            getattr(translation, details['reference'][2]).set([obj])

        for lang, message in details['langs'].items():
            Translation.objects.edit_translation_by_id(
                translation.id,
                lang,
                message[0],
                manual=message[1]
            )


def translation_ids(model):
    ids = []
    for obj in model.objects.all():
        for field in model.objects.translated_fields:
            ids.append(getattr(obj, field).id)

    return ids
