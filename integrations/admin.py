from django.contrib import admin
from unfold.admin import ModelAdmin
from integrations.models import Link


class LinkAdmin(ModelAdmin):
    search_fields = ("link",)
    list_display = ["validated", "valid_status_code", "status_code", "in_use", "link"]


admin.site.register(Link, LinkAdmin)
