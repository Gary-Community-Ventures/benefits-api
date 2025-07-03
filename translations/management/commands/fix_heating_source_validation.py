from django.core.management.base import BaseCommand
from translations.models import Translation
from django.conf import settings


class Command(BaseCommand):
    help = """
    Fix the validation message for heating source selection.
    Changes "Please select a gas provider" to "Please select a heating source"
    """

    def handle(self, *args, **options):
        # Search for translations that might contain the wrong message
        translations = Translation.objects.prefetch_related('translations').all()
        
        found_translations = []
        
        # Search for translations containing "gas provider" text
        for translation in translations:
            for lang in [lang['code'] for lang in settings.PARLER_LANGUAGES[None]]:
                translation.set_current_language(lang)
                if translation.text and "gas provider" in translation.text.lower():
                    found_translations.append({
                        'id': translation.id,
                        'label': translation.label,
                        'lang': lang,
                        'text': translation.text
                    })
        
        if not found_translations:
            self.stdout.write(self.style.WARNING('No translations found containing "gas provider"'))
            return
        
        # Display found translations
        self.stdout.write(self.style.SUCCESS(f'Found {len(found_translations)} translations containing "gas provider":'))
        for t in found_translations:
            self.stdout.write(f"ID: {t['id']}, Label: {t['label']}, Lang: {t['lang']}, Text: {t['text']}")
        
        # Look for the specific validation message
        for t in found_translations:
            if t['text'] == "Please select a gas provider":
                self.stdout.write(self.style.SUCCESS(f"\nFound exact match for validation message:"))
                self.stdout.write(f"Translation ID: {t['id']}, Label: {t['label']}")
                
                # Update the translation
                translation = Translation.objects.get(pk=t['id'])
                translation.set_current_language(t['lang'])
                
                # Update to the correct message
                Translation.objects.edit_translation_by_id(
                    t['id'], 
                    t['lang'], 
                    "Please select a heating source",
                    manual=True
                )
                
                self.stdout.write(self.style.SUCCESS('Updated translation to "Please select a heating source"'))
                
                # Update all language versions if this is the default language
                if t['lang'] == settings.LANGUAGE_CODE:
                    self.stdout.write('Updating other language versions...')
                    
                    # Define translations for common languages
                    translations_map = {
                        'es': 'Por favor seleccione una fuente de calefacción',
                        'vi': 'Vui lòng chọn nguồn sưởi ấm',
                        'fr': 'Veuillez sélectionner une source de chauffage',
                        'zh': '请选择供暖源',
                        'ar': 'يرجى اختيار مصدر التدفئة',
                        'ru': 'Пожалуйста, выберите источник отопления',
                        'ne': 'कृपया तताउने स्रोत चयन गर्नुहोस्',
                        'am': 'እባክዎን የማሞቂያ ምንጭ ይምረጡ',
                        'so': 'Fadlan dooro isha kuleylka',
                        'my': 'အပူပေးစနစ်ကို ရွေးချယ်ပါ',
                        'sw': 'Tafadhali chagua chanzo cha joto'
                    }
                    
                    for lang_code, translated_text in translations_map.items():
                        if lang_code in [lang['code'] for lang in settings.PARLER_LANGUAGES[None]]:
                            Translation.objects.edit_translation_by_id(
                                t['id'],
                                lang_code,
                                translated_text,
                                manual=False
                            )
                            self.stdout.write(f'Updated {lang_code} translation')
                
                return
        
        # If exact match not found, show instructions
        self.stdout.write(self.style.WARNING('\nExact validation message not found.'))
        self.stdout.write('You may need to:')
        self.stdout.write('1. Check the frontend code to find the exact translation label being used')
        self.stdout.write('2. Manually update the translation via the admin interface')
        self.stdout.write('3. Or create a new translation with the correct message')