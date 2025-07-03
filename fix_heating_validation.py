#!/usr/bin/env python
"""
Standalone script to fix the heating source validation message.
Run from the project root: python fix_heating_validation.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benefits.settings')
django.setup()

from translations.models import Translation
from django.conf import settings


def main():
    print("Fixing Heating Source Validation Message")
    print("=" * 50)
    
    # Search for translations containing "gas provider"
    found_translations = []
    translations = Translation.objects.prefetch_related('translations').all()
    
    print("Searching for translations containing 'gas provider'...")
    
    for translation in translations:
        for lang in [lang['code'] for lang in settings.PARLER_LANGUAGES[None]]:
            translation.set_current_language(lang)
            if translation.text and "gas provider" in translation.text.lower():
                found_translations.append({
                    'id': translation.id,
                    'label': translation.label,
                    'lang': lang,
                    'text': translation.text,
                    'translation_obj': translation
                })
    
    if not found_translations:
        print("\nNo translations found containing 'gas provider'")
        print("\nThis might mean:")
        print("1. The text is hardcoded in the frontend")
        print("2. The translation uses a different wording")
        print("3. The translation hasn't been created yet")
        
        # Create a new translation
        print("\nWould you like to create a new translation? (y/n): ", end='')
        if input().lower() == 'y':
            label = input("Enter a label for the translation (e.g., 'validation.heating_source'): ")
            translation = Translation.objects.add_translation(
                label, 
                "Please select a heating source",
                active=True
            )
            print(f"\nCreated new translation with label: {label}")
            print(f"Translation ID: {translation.id}")
        return
    
    # Display found translations
    print(f"\nFound {len(found_translations)} translations containing 'gas provider':")
    for i, t in enumerate(found_translations):
        print(f"\n{i+1}. ID: {t['id']}, Label: {t['label']}, Lang: {t['lang']}")
        print(f"   Text: {t['text']}")
    
    # Look for exact match
    exact_match = None
    for t in found_translations:
        if t['text'] == "Please select a gas provider":
            exact_match = t
            break
    
    if exact_match:
        print(f"\n✓ Found exact match!")
        print(f"  Translation ID: {exact_match['id']}")
        print(f"  Label: {exact_match['label']}")
        
        print("\nUpdating to 'Please select a heating source'...")
        
        # Update the translation
        Translation.objects.edit_translation_by_id(
            exact_match['id'], 
            exact_match['lang'], 
            "Please select a heating source",
            manual=True
        )
        
        print("✓ Updated successfully!")
        
        # Update other languages if this is the default language
        if exact_match['lang'] == settings.LANGUAGE_CODE:
            print("\nUpdating translations for other languages...")
            
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
                    try:
                        Translation.objects.edit_translation_by_id(
                            exact_match['id'],
                            lang_code,
                            translated_text,
                            manual=False
                        )
                        print(f"  ✓ Updated {lang_code} translation")
                    except Exception as e:
                        print(f"  ✗ Failed to update {lang_code}: {str(e)}")
        
        print("\n✓ All updates complete!")
        print("\nNext steps:")
        print("1. Clear any caches (Redis, browser cache)")
        print("2. Restart the application if needed")
        print("3. Test the form to verify the fix")
        
    else:
        print("\n✗ No exact match found for 'Please select a gas provider'")
        print("\nWould you like to update one of the found translations? (y/n): ", end='')
        
        if input().lower() == 'y':
            print("\nEnter the number of the translation to update: ", end='')
            try:
                choice = int(input()) - 1
                if 0 <= choice < len(found_translations):
                    selected = found_translations[choice]
                    Translation.objects.edit_translation_by_id(
                        selected['id'],
                        selected['lang'],
                        "Please select a heating source",
                        manual=True
                    )
                    print(f"\n✓ Updated translation ID {selected['id']} successfully!")
                else:
                    print("\n✗ Invalid selection")
            except ValueError:
                print("\n✗ Invalid input")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)