from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Configuration


class ConfigurationAdmin(ModelAdmin):
    search_fields = ('name',)


admin.site.register(Configuration, ConfigurationAdmin)
