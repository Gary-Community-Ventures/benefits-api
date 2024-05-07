from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Translation


class TranslationAdmin(TranslatableAdmin):
    search_fields = ("label",)


admin.site.register(Translation, TranslatableAdmin)
