from django.core.management.base import BaseCommand
from integrations.services.google_translate.integration import Translate
from collections import defaultdict
from django.apps import apps
from django.conf import settings
from tqdm import tqdm


class Command(BaseCommand):
    help = "Urgent need types and program categories data sync"

    URGENT_NEED_TYPE_MAP = {
        3: {
            1: "Food or groceries",
            3: "Behavioral health",
            5: "Child's development",
            6: "Civil legal needs",
            8: "Managing housing costs",
            9: "Family planning or birth control",
            10: "Food or groceries",
            11: "Low-cost dental care",
            13: "Baby supplies",
            14: "Managing housing costs",
            15: "Funeral, burial, or cremation costs",
            16: "Managing housing costs",
            17: "Food or groceries",
            22: "Child's development",
            23: "Job resources",
            24: "Civil legal needs",
            25: "Baby supplies",
            26: "Managing housing costs",
            31: "Behavioral health",
            39: "Managing housing costs",
            45: "Managing housing costs",
            46: "Child's development",
            47: "Behavioral health",
            62: "Job resources",
            63: "Food or groceries",
            69: "Child's development",
            74: "Managing housing costs",
            75: "Child's development",
            83: "Family planning",
            88: "Managing housing costs",
        },
        4: {
            2: "Managing housing costs",
            7: "Behavioral health",
            12: "Civil legal needs",
            21: "Managing housing costs",
            27: "Managing housing costs",
            28: "Child's development",
            29: "Behavioral health",
            30: "Managing housing costs",
            32: "Managing housing costs",
            33: "Child's development",
            34: "Managing housing costs",
            35: "Behavioral health",
            36: "Managing housing costs",
            37: "Managing housing costs",
            38: "Baby supplies",
            40: "Child's development",
            41: "Behavioral health",
            42: "Managing housing costs",
            43: "Baby supplies",
            48: "Child's development",
            49: "Managing housing costs",
            50: "Behavioral health",
            51: "Baby supplies",
            52: "Civil legal needs",
            53: "Managing housing costs",
            54: "Child's development",
            55: "Behavioral health",
            57: "Family planning",
            58: "Civil legal needs",
            59: "Managing housing costs",
            61: "Job resources",
            64: "Job resources",
            65: "Family planning",
            66: "Behavioral health",
            67: "Managing housing costs",
            68: "Food or groceries",
            70: "Managing housing costs",
            71: "Managing housing costs",
            72: "Child's development",
            73: "Behavioral health",
            76: "Child's development",
            77: "Managing housing costs",
            78: "Child's development",
            79: "Managing housing costs",
            80: "Behavioral health",
            81: "Managing housing costs",
            84: "Child's development",
            85: "Managing housing costs",
            86: "Managing housing costs",
            91: "Behavioral health",
            92: "Low-cost dental care",
            101: "Low-cost dental care",
        },
        5: {
            4: "Food or groceries",
            18: "Managing housing costs",
            19: "Managing housing costs",
            20: "Managing housing costs",
            44: "Managing housing costs",
            56: "Baby supplies",
            60: "Civil legal needs",
            82: "Low-cost dental care",
            87: "Job resources",
            89: "Child's development",
            90: "Job resources",
            93: "Managing housing costs",
            94: "Veterans resources",
            95: "Veterans resources",
            96: "Child's development",
            97: "Veterans resources",
            98: "Behavioral health",
            99: "Managing housing costs",
            100: "Child's development",
            102: "Family planning",
            103: "Civil legal needs",
            104: "Civil legal needs",
            105: "Managing housing costs",
        },
    }

    PROGRAM_CATEGORY_ICON_MAP = {
        7: {1: "tax_credit"},
        6: {2: "talk", 3: "heat", 4: "low_fuel", 5: "light_bulb"},
        4: {6: "housing", 7: "cash", 8: "food", 9: "health_care", 10: "tax_credit", 13: "child_care"},
        3: {
            11: "transportation",
            12: "housing",
            14: "cash",
            15: "food",
            16: "child_care",
            17: "health_care",
            18: "tax_credit",
        },
        5: {
            19: "tax_credit",
            20: "transportation",
            21: "housing",
            22: "health_care",
            23: "child_care",
            24: "cash",
            25: "food",
        },
    }

    def handle(self, *args, **options):
        UrgentNeed = apps.get_model("programs", "UrgentNeed")
        Translation = apps.get_model("translations", "Translation")
        UrgentNeedType = apps.get_model("programs", "UrgentNeedType")
        CategoryIconName = apps.get_model("programs", "CategoryIconName")
        WhiteLabel = apps.get_model("screener", "WhiteLabel")
        ProgramCategory = apps.get_model("programs", "ProgramCategory")

        # {white_label_id: {urgent_need_id: type_name}}
        urgent_need_type_mapping = defaultdict(dict, self.URGENT_NEED_TYPE_MAP)

        # {white_label_id: {program_category_id: icon_name}}
        program_category_icon_mapping = defaultdict(dict, self.PROGRAM_CATEGORY_ICON_MAP)

        need_type_lookup = defaultdict(dict)

        # Create Urgent Need Types for each white label based on the mapping.
        for wl_id, type_dict in tqdm(urgent_need_type_mapping.items(), desc="Urgent Need Types"):
            white_label = WhiteLabel.objects.get(id=wl_id)
            for need_id, type_name in type_dict.items():
                icon = CategoryIconName.objects.filter(name__iexact=type_name).first()

                need_type = UrgentNeedType.objects.filter(
                    white_label=white_label, name__translations__text__iexact=type_name.strip()
                ).first()

                if not need_type:
                    need_type = UrgentNeedType.objects.new_urgent_need_type(white_label=white_label.code, icon=icon)
                    # translate the 'name' field
                    base_lang = "en-us"
                    name_translation = need_type.name

                    Translation.objects.edit_translation_by_id(name_translation.id, base_lang, type_name)

                    for lang_code, _ in settings.LANGUAGES:
                        if lang_code == base_lang:
                            continue
                        auto_translated = Translate().translate(lang_code, type_name)
                        translated_obj = Translation.objects.edit_translation_by_id(
                            name_translation.id, lang_code, auto_translated
                        )
                        translated_obj.edited = False
                        translated_obj.save()

                need_type_lookup[need_id] = need_type.id

            # Assign the urgent need types to the urgent needs.
            for need in UrgentNeed.objects.filter(white_label=white_label):
                category_type = UrgentNeedType.objects.get(id=need_type_lookup.get(need.id))
                need.category_type = category_type
                need.save()

        # Assign program category icons based on the mapping.
        for wl_id, icon_dict in tqdm(program_category_icon_mapping.items(), desc="Program Category Icons"):
            white_label = WhiteLabel.objects.get(id=wl_id)
            for category_id, icon_name in icon_dict.items():
                icon = CategoryIconName.objects.filter(name__iexact=icon_name).first()
                category = ProgramCategory.objects.filter(white_label=white_label, id=category_id).first()

                category.icon = icon
                category.save()
