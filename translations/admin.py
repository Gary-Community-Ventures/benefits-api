from django.contrib import admin
from parler.admin import TranslatableAdmin
from unfold.admin import ModelAdmin
from .models import Translation


@admin.register(Translation)
class TranslationAdmin(ModelAdmin, TranslatableAdmin):
    search_fields = ('label',)
    list_display = ['label', 'category', 'no_auto',
                    'edited', 'active',]

    def label(self, obj):
        return obj.label.split('.')[1] if '.' in obj.label else obj.label

    def category(self, obj):
        return obj.label.split('.')[0] if '.' in obj.label else ''

    category.admin_order_field = 'label'


# admin.site.register(Translation, TranslationAdmin)
