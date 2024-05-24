from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Message,
    Screen,
    IncomeStream,
)


class screenAdmin(ModelAdmin):
    search_fields = ('id',)


class CustomMessageAdmin(ModelAdmin):
    pass


class CustomIncomeStreamAdmin(ModelAdmin):
    pass


admin.site.register(Screen, screenAdmin)
admin.site.register(Message, CustomMessageAdmin)
admin.site.register(IncomeStream, CustomIncomeStreamAdmin)
