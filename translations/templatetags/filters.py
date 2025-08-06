from django import template
from django.conf import settings

register = template.Library()


@register.filter
def get_updated_label(updated_dates, lang_code, default="Never"):
    return updated_dates.get(lang_code, default)


@register.filter
def get_update_type(translation, lang_code):
    for record in translation.translations.all():
        if record.language_code == lang_code:
            return record.edited


@register.filter
def get_language_name(lang_code):
    return dict(settings.LANGUAGES).get(lang_code, lang_code)
