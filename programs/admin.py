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
    UrgentNeedCategory,
    NavigatorCounty,
    Document,
)


class ProgramAdmin(admin.ModelAdmin):
    search_fields = ('name_abbreviated',)


class LegalStatusAdmin(admin.ModelAdmin):
    search_fields = ('status',)


class NavigatorCountiesAdmin(admin.ModelAdmin):
    search_fields = ('name',)


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


class DocumentAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class ReferrerAdmin(admin.ModelAdmin):
    search_fields = ('referrer_code',)


class WebHookFunctionsAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(LegalStatus, LegalStatusAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(NavigatorCounty, NavigatorCountiesAdmin)
admin.site.register(Navigator, NavigatorAdmin)
admin.site.register(UrgentNeed, UrgentNeedAdmin)
admin.site.register(UrgentNeedCategory, UrgentNeedCategoryAdmin)
admin.site.register(UrgentNeedFunction, UrgentNeedFunctionAdmin)
admin.site.register(FederalPoveryLimit, FederalPovertyLimitAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Referrer, ReferrerAdmin)
admin.site.register(WebHookFunction, WebHookFunctionsAdmin)
