# TODO: add translation override model
from programs.util import Dependencies
from screener.models import Screen

class TranslationOverrideCalculator:
  dependencies = tuple()

  def _init_(self, screen: Screen, translation_override, missing_dependencies: Dependencies):
    self.screen = screen
    self.translation_override = translation_override
    self.missing_dependencies = missing_dependencies

  def calc(self) -> bool:
    """
    Return if the translation should be overridden
    """
    if not self.can_calc():
      return False

    return self.eligible()

  def eligible(self) -> bool:
    """
    Custom requirement for whether or not to override the Translation
    """
    return True

  def can_calc(self) -> bool:
    """
    Returns whether or not we can calculate if a translation can be overriden
    """
    return not self.missing_dependencies.has(*self.dependencies)

  # TODO: county eligible method after the model is defined
