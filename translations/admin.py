from django.contrib import admin
from django.urls import reverse_lazy
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import Translation


class TranslationAdmin(ModelAdmin, TranslatableAdmin):
    search_fields = ('label',)
    list_display = ['label', 'used_by', 'no_auto',
                    'edited', 'active', 'go_to']

    def used_by(self, obj):
        return obj.used_by
    
    used_by.short_description = 'Used by (Model)'

    def go_to(self, obj):
        url = reverse_lazy('translation_admin_url', args=[obj.pk])
        return format_html('<a href="{}">Label</a>', url)

    go_to.short_description = 'Translate:'


admin.site.register(Translation, TranslationAdmin)
