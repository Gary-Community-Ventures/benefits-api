from django.contrib import admin
from .models import Configuration, StateSpecificModifier

class ConfigurationAdmin(admin.ModelAdmin):
    search_fields = ('name',)

admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(StateSpecificModifier, ConfigurationAdmin)