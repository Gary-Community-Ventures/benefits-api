from django.conf import settings
from decouple import config
import json
from google.oauth2 import service_account
from google.cloud import translate_v2 as translate
import html


class Translate:
    """
    Google Translate integration for the benefits API.

    This class preserves paragraph structure by splitting input text into paragraphs before translation
    and joining them after translation. This ensures that multi-paragraph texts retain their original
    formatting when translated. All translation entry points (single and bulk) use this logic.
    """

    main_language: str = settings.LANGUAGE_CODE
    languages: list[str] = [
        lang["code"] for lang in settings.PARLER_LANGUAGES[None] if lang["code"] != settings.LANGUAGE_CODE
    ]

    @staticmethod
    def split_paragraphs(text):
        """
        Splits text into paragraphs using two or more consecutive newlines as delimiters.
        Preserves empty paragraphs and leading/trailing whitespace.
        """
        # Normalize newlines
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        # Split on two or more newlines
        paragraphs = normalized.split("\n")
        return paragraphs

    @staticmethod
    def join_paragraphs(paragraphs):
        """
        Joins paragraphs with two newlines to preserve paragraph breaks.
        """
        return "\n".join(paragraphs)

    def __init__(self):
        info = json.loads(config("GOOGLE_APPLICATION_CREDENTIALS"))
        creds = service_account.Credentials.from_service_account_info(info)
        self.client = translate.Client(credentials=creds)

    def translate(self, lang: str, text: str):
        """
        Translates the text from the default language to the lang param language, preserving paragraph structure.
        """
        if lang not in Translate.languages:
            raise Exception(f"{lang} is not configured in settings, or is the default language")

        # Short-circuit for empty string
        if text == "":
            return ""

        # Delegate to bulk_translate for consistency and DRYness
        result = self.bulk_translate([lang], [text])
        return result[text][lang]

    def bulk_translate(self, langs: list[str], texts: list[str]):
        """
        Translates all of the texts to the target langs, preserving paragraph structure for each text.
        Include __all__ in langs to translate to all languages.
        """
        if "__all__" in langs:
            langs = Translate.languages

        translations = {text: {} for text in texts}
        for lang in langs:
            if lang not in Translate.languages:
                raise Exception(f"{lang} is not configured in settings, or is the default language")

            # For each text, split into paragraphs, translate, and rejoin
            for text in texts:
                paragraphs = self.split_paragraphs(text)

                try:
                    results = self.client.translate(
                        paragraphs, target_language=lang, source_language=Translate.main_language
                    )
                except Exception as e:
                    capture_exception(e, level="error")
                    raise
                if isinstance(results, dict):
                    translated_paragraphs = [self.format_text(results)]
                else:
                    translated_paragraphs = [self.format_text(res) for res in results]
                translations[text][lang] = self.join_paragraphs(translated_paragraphs)
        return translations

    def format_text(self, result):
        # If the input is whitespace-only, return it unchanged
        if result["input"].strip() == "":
            return result["input"]
        leading_spaces = len(result["input"]) - len(result["input"].lstrip(" "))
        trailing_spaces = len(result["input"]) - len(result["input"].rstrip(" "))
        return " " * leading_spaces + html.unescape(result["translatedText"]).strip() + " " * trailing_spaces
