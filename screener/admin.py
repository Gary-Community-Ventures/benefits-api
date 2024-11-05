from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Message,
    Screen,
    IncomeStream,
    WhiteLabel,
)


class WhiteLabelAdmin(ModelAdmin):
    search_fields = ("name",)


class ScreenAdmin(ModelAdmin):
    search_fields = ("id",)


class CustomMessageAdmin(ModelAdmin):
    pass


class CustomIncomeStreamAdmin(ModelAdmin):
    pass


admin.site.register(WhiteLabel, WhiteLabelAdmin)
admin.site.register(Screen, ScreenAdmin)
admin.site.register(Message, CustomMessageAdmin)
admin.site.register(IncomeStream, CustomIncomeStreamAdmin)
