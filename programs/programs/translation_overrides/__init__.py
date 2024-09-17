from programs.programs.translation_overrides.dont_show import DontShow
from .base import TranslationOverrideCalculator

general_calculators: dict[str, type[TranslationOverrideCalculator]] = {
  "_show": TranslationOverrideCalculator,
  "_dont_show": DontShow,
}

specific_calculators: dict[str, type[TranslationOverrideCalculator]] = {}

warning_calculators: dict[str, type[TranslationOverrideCalculator]] = {**general_calculators, **specific_calculators}