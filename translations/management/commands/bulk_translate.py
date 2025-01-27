from django.core.management.base import BaseCommand
from django.conf import settings
from translations.models import Translation
from integrations.services.google_translate.integration import Translate


class Command(BaseCommand):
    help = """
    Get translation export
    """

    def add_arguments(self, parser):
        parser.add_argument("--limit", default=1, type=int)
        parser.add_argument("--all", default=False, type=bool)
        parser.add_argument("--lang", default=settings.LANGUAGE_CODE, type=str)

    def handle(self, *args, **options):
        limit = 10_000 if options["all"] else min(10_000, options["limit"])
        max_batch_size = 128
        char_limit = 5_000
        lang = options["lang"]

        translate = Translate()

        translations = Translation.objects.prefetch_related("translations").language(settings.LANGUAGE_CODE).all()

        total_count = 0
        temp_chars = 0
        temp_count = 0
        texts = {}
        batches = []
        for translation in translations:
            text = translation.text
            current_translation = translation.get_lang(lang)
            is_edited = current_translation is not None and current_translation.edited
            if is_edited or translation.text is None:
                continue

            if translation.no_auto:
                translation.set_current_language(lang)
                translation.text = text
                translation.save()
                continue

            if temp_chars + len(text) > char_limit or temp_count + 1 > max_batch_size:
                batches.append(texts.copy())
                texts = {}
                temp_chars = 0
                temp_count = 0

            temp_chars += len(text)
            temp_count += 1
            total_count += 1

            if text not in texts:
                texts[text] = []
            texts[text].append(translation)

            if total_count >= limit:
                batches.append(texts)
                break

        for batch in batches:
            auto = translate.bulk_translate([lang], list(batch.keys()))
            for [original_text, new_text] in auto.items():
                for trans in batch[original_text]:
                    Translation.objects.edit_translation_by_id(trans.id, lang, new_text[lang], manual=False)
