from django.contrib import admin
from unfold.admin import ModelAdmin
from django_json_widget.widgets import JSONEditorWidget
from django.db.models import JSONField
from .models import Configuration
import json


class ConfigurationAdmin(ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget(
            options={
                'modes': ['tree', 'code'],
                'mode': 'tree',
                'enableDrag': False
            }
        )},
    }
    search_fields = ("name",)

    # Convert the JSON string to a dictionary
    # This makes it so that the JSON data coming from the 'data' field of the Configuration model
    # is displayed as a dictionary and without the escape characters
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and isinstance(obj.data, str):
            obj.data = json.loads(obj.data)
        return form


admin.site.register(Configuration, ConfigurationAdmin)
