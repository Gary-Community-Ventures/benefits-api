from django.conf import settings
from decouple import config
import json
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate


class Translate():
    languages: list[str] = [lang['code'] for lang in settings.PARLER_LANGUAGES[None]]
    main_language: str = settings.LANGUAGE_CODE
    languages.remove(main_language)

    def __init__(self):
        info = json.loads(config('GOOGLE_APPLICATION_CREDENTIALS'))
        creds = service_account.Credentials.from_service_account_info(info)
        self.client = translate.Client(credentials=creds)

    def translate(self, lang: str, text: str):
        '''
        Translates the text from the default language to the lang param language.
        '''
        if lang not in Translate.languages:
            raise Exception(f'{lang} is not configured in settings.')

        result = self.client.translate(text, target_language=lang, source_language=Translate.main_language)

        return result['translatedText']

    def bulk_translate(self, langs: list[str], texts: list[str]):
        '''
        Translates all of the texts to the target langs.
        Include __all__ in langs to tranlsate to all languages.
        '''
        if '__all__' in langs:
            langs = Translate.languages

        translations = {text: {} for text in texts}
        for lang in langs:
            if lang not in Translate.languages:
                raise Exception(f'{lang} is not configured in settings.')

            results = self.client.translate(texts, target_language=lang, source_language=Translate.main_language)

            for result in results:
                translations[result['input']][lang] = result['translatedText']

        return translations
