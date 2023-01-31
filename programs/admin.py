from django.contrib import admin
from .models import Program, UrgentNeed, Navigator
from parler.admin import TranslatableAdmin


class ProgramAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)


class UrgentNeedsAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)
    fields = ('name', 'description', 'link', 'type',
              'phone_number', 'type_short', 'active')


class NavigatorAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)


admin.site.register(Program, ProgramAdmin)
admin.site.register(UrgentNeed, UrgentNeedsAdmin)
admin.site.register(Navigator, NavigatorAdmin)
