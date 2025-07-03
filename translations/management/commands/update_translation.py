from django.core.management.base import BaseCommand
from translations.models import Translation
from django.conf import settings
import argparse


class Command(BaseCommand):
    help = """
    Search for and optionally update translations.
    
    Examples:
    - Search for translations: python manage.py update_translation --search "gas provider"
    - Update a specific translation: python manage.py update_translation --label "validation.gas_provider" --text "Please select a heating source"
    - Update by ID: python manage.py update_translation --id 123 --text "Please select a heating source"
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--search',
            type=str,
            help='Search for translations containing this text (case-insensitive)'
        )
        parser.add_argument(
            '--label',
            type=str,
            help='The label of the translation to update'
        )
        parser.add_argument(
            '--id',
            type=int,
            help='The ID of the translation to update'
        )
        parser.add_argument(
            '--text',
            type=str,
            help='The new text for the translation'
        )
        parser.add_argument(
            '--lang',
            type=str,
            default=settings.LANGUAGE_CODE,
            help='Language code (default: en-us)'
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create a new translation if it doesn\'t exist (only works with --label)'
        )

    def handle(self, *args, **options):
        if options['search']:
            self.search_translations(options['search'])
        
        if options['text'] and (options['label'] or options['id']):
            self.update_translation(
                label=options['label'],
                translation_id=options['id'],
                text=options['text'],
                lang=options['lang'],
                create=options['create']
            )
        elif not options['search']:
            self.stdout.write(self.style.ERROR('Please provide either --search or --text with --label/--id'))

    def search_translations(self, search_text):
        """Search for translations containing the given text."""
        translations = Translation.objects.prefetch_related('translations').all()
        found_translations = []
        
        for translation in translations:
            for lang in [lang['code'] for lang in settings.PARLER_LANGUAGES[None]]:
                translation.set_current_language(lang)
                if translation.text and search_text.lower() in translation.text.lower():
                    found_translations.append({
                        'id': translation.id,
                        'label': translation.label,
                        'lang': lang,
                        'text': translation.text,
                        'active': translation.active
                    })
        
        if not found_translations:
            self.stdout.write(self.style.WARNING(f'No translations found containing "{search_text}"'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(found_translations)} translations containing "{search_text}":'))
        self.stdout.write('-' * 80)
        
        for t in found_translations:
            self.stdout.write(f"ID: {t['id']}")
            self.stdout.write(f"Label: {t['label']}")
            self.stdout.write(f"Language: {t['lang']}")
            self.stdout.write(f"Active: {t['active']}")
            self.stdout.write(f"Text: {t['text']}")
            self.stdout.write('-' * 80)

    def update_translation(self, label=None, translation_id=None, text=None, lang=None, create=False):
        """Update a translation by label or ID."""
        try:
            if translation_id:
                translation = Translation.objects.get(pk=translation_id)
                self.stdout.write(f'Found translation by ID: {translation_id}')
            elif label:
                try:
                    translation = Translation.objects.get(label=label)
                    self.stdout.write(f'Found translation by label: {label}')
                except Translation.DoesNotExist:
                    if create:
                        translation = Translation.objects.add_translation(label, text)
                        self.stdout.write(self.style.SUCCESS(f'Created new translation with label: {label}'))
                        return
                    else:
                        self.stdout.write(self.style.ERROR(f'Translation with label "{label}" not found. Use --create to create it.'))
                        return
            else:
                self.stdout.write(self.style.ERROR('Please provide either --label or --id'))
                return
            
            # Update the translation
            old_text = translation.get_lang(lang).text if translation.get_lang(lang) else None
            Translation.objects.edit_translation_by_id(translation.id, lang, text, manual=True)
            
            self.stdout.write(self.style.SUCCESS(f'Updated translation:'))
            self.stdout.write(f'  Label: {translation.label}')
            self.stdout.write(f'  Language: {lang}')
            self.stdout.write(f'  Old text: {old_text}')
            self.stdout.write(f'  New text: {text}')
            
        except Translation.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Translation not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error updating translation: {str(e)}'))