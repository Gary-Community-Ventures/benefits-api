from django.contrib import admin
from .models import (
    LegalStatus,
    Program,
    UrgentNeed,
    Navigator,
    UrgentNeedFunction,
    FederalPoveryLimit,
    Referrer,
    WebHookFunction,
    UrgentNeedCategory
)
from parler.admin import TranslatableAdmin


class ProgramAdmin(admin.ModelAdmin):
    search_fields = ('name_abbreviated',)


class LegalStatusAdmin(admin.ModelAdmin):
    search_fields = ('status',)


class NavigatorAdmin(admin.ModelAdmin):
    search_fields = ('translations__name',)


class UrgentNeedAdmin(admin.ModelAdmin):
    search_fields = ('translations__name',)


class UrgentNeedCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    fields = ('name',)


class UrgentNeedFunctionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    fields = ('name',)


class FederalPovertyLimitAdmin(admin.ModelAdmin):
    search_fields = ('year',)


class ReferrerAdmin(TranslatableAdmin):
    search_fields = ('referrer_code',)


class WebHookFunctionsAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(LegalStatus, LegalStatusAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Navigator, NavigatorAdmin)
admin.site.register(UrgentNeed, UrgentNeedAdmin)
admin.site.register(UrgentNeedCategory, UrgentNeedCategoryAdmin)
admin.site.register(UrgentNeedFunction, UrgentNeedFunctionAdmin)
admin.site.register(FederalPoveryLimit, FederalPovertyLimitAdmin)
admin.site.register(Referrer, ReferrerAdmin)
admin.site.register(WebHookFunction, WebHookFunctionsAdmin)
