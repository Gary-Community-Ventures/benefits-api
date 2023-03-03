from django.contrib import admin
from .models import Program, UrgentNeed, Navigator, UrgentNeedFunction
from parler.admin import TranslatableAdmin


class ProgramAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)


class NavigatorAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)


class UrgentNeedAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)
    fields = ('name', 'description', 'link', 'type',
              'phone_number', 'type_short', 'active', 'functions')


class UrgentNeedsFunctionAdmin(admin.ModelAdmin):
    search_fields = ('function_name',)
    fields = ('function_name',)


admin.site.register(Program, ProgramAdmin)
admin.site.register(Navigator, NavigatorAdmin)
admin.site.register(UrgentNeed, UrgentNeedAdmin)
admin.site.register(UrgentNeedFunction, UrgentNeedsFunctionAdmin)
