from django.contrib import admin

from .models import Program
from parler.admin import TranslatableAdmin


class ProgramAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)

admin.site.register(Program, ProgramAdmin)