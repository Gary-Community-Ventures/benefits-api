from django.contrib import admin
from .models import Program, Navigator
from parler.admin import TranslatableAdmin


class ProgramAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)

class NavigatorAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)

admin.site.register(Program, ProgramAdmin)
admin.site.register(Navigator, NavigatorAdmin)
