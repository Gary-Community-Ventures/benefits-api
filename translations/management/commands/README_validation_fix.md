# Fixing the Heating Source Validation Message

## Issue Summary
On Step 7 "Tell us about your utilities", when selecting a heating source (e.g., Atmos Energy), the form displays an incorrect validation message "Please select a gas provider" instead of "Please select a heating source".

## Resolution Steps

### Option 1: Automated Fix (if exact translation exists)
Run the following command to automatically search for and fix the validation message:

```bash
python manage.py fix_heating_source_validation
```

This command will:
- Search for all translations containing "gas provider"
- Find the exact match "Please select a gas provider"
- Update it to "Please select a heating source"
- Update translations for all supported languages

### Option 2: Manual Search and Update
If the automated fix doesn't find the exact translation, use the flexible update command:

1. **Search for translations containing "gas provider":**
   ```bash
   python manage.py update_translation --search "gas provider"
   ```

2. **Once you find the correct translation ID or label, update it:**
   ```bash
   # Update by ID
   python manage.py update_translation --id [TRANSLATION_ID] --text "Please select a heating source"
   
   # Or update by label
   python manage.py update_translation --label "[TRANSLATION_LABEL]" --text "Please select a heating source"
   ```

### Option 3: Create a New Translation
If the translation doesn't exist in the database (frontend might be using hardcoded text):

```bash
python manage.py update_translation --label "validation.heating_source" --text "Please select a heating source" --create
```

## Frontend Integration Notes

The frontend likely uses one of these patterns to fetch the validation message:
- Direct translation label reference: `translations['validation.gas_provider']`
- Component-specific validation: `energyCalculator.validation.gasProvider`

To determine the exact label being used:
1. Check the frontend React/JavaScript code for the utilities form component
2. Look for translation keys in the validation logic
3. Search for "Please select a gas provider" in the frontend codebase

## Additional Considerations

1. **Cache Invalidation**: After updating translations, the translation cache will be automatically invalidated. The frontend may need to refresh its cache or be redeployed.

2. **Multi-language Support**: The automated fix includes translations for:
   - Spanish: "Por favor seleccione una fuente de calefacción"
   - Vietnamese: "Vui lòng chọn nguồn sưởi ấm"
   - French: "Veuillez sélectionner une source de chauffage"
   - And other supported languages

3. **Validation Logic**: The actual validation logic (when to show the error) is handled by the frontend. This fix only updates the message text.

## Verification

After applying the fix:
1. Clear browser cache
2. Navigate to Step 7 of the form
3. Select a heating source (e.g., Atmos Energy)
4. Verify that no error appears or the correct message is shown