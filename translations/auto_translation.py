from django.conf import settings
from decouple import config
import json
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate


class Translate():
    languages = tuple(map(lambda l: l['code'], settings.PARLER_LANGUAGES[None]))
    main_language = settings.LANGUAGE_CODE

    def __init__(self):
        info = json.loads(config('GOOGLE_APPLICATION_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(info)
        client = translate.Client(credentials=creds)
        # print(client.get_supported_languages(parent='projects/benefits-358119'))
        result = client.translate('hello', target_language='es')

        print("Text: {}".format(result["input"]))
        print("Translation: {}".format(result["translatedText"]))
        print("Detected source language: {}".format(result["detectedSourceLanguage"]))
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
