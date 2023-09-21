from django.conf import settings
from decouple import config
from google.cloud import translate


class Translate():
    languages = tuple(map(lambda l: l['code'], settings.PARLER_LANGUAGES[None]))
    main_language = settings.LANGUAGE_CODE

    def __init__(self):
        client = translate.TranslationServiceClient.from_service_account_json('./google_credentials.json')
        print(client.get_supported_languages(parent='projects/benefits-358119'))
        # response = client.translate_text(
        #     parent='projects/benefits-358119',
        #     contents=['hello'],
        #     mime_type="text/plain",  # mime types: text/plain, text/html
        #     source_language_code="en-US",
        #     target_language_code="fr",
        # )
        # for translation in response.translations:
        #     print(f"Translated text: {translation.translated_text}")

    def translate(self, lang, text):
        pass

    def bulk_tranlsate(self, langs, text):
        pass
