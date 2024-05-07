from django.contrib import admin
from .models import (
    Message,
    Screen,
    IncomeStream,
)


class screenAdmin(admin.ModelAdmin):
    search_fields = ("id",)


admin.site.register(Screen, screenAdmin)
admin.site.register(Message)
admin.site.register(IncomeStream)
