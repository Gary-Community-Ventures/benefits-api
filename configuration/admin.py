from django.contrib import admin
from .models import Configuration

class ConfigurationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

admin.site.register(Configuration, ConfigurationAdmin)