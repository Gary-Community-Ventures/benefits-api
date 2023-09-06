from django.contrib import admin
from .models import Program, UrgentNeed, Navigator, UrgentNeedFunction, FederalPoveryLimit, Referrer, WebHookFunction
from parler.admin import TranslatableAdmin


class ProgramAdmin(admin.ModelAdmin):
    search_fields = ('name_abbreviated',)


class NavigatorAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)


class UrgentNeedAdmin(TranslatableAdmin):
    search_fields = ('translations__name',)


class UrgentNeedsFunctionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    fields = ('name',)


class FederalPovertyLimitAdmin(admin.ModelAdmin):
    search_fields = ('year',)


class ReferrerAdmin(TranslatableAdmin):
    search_fields = ('referrer_code',)


class WebHookFunctionsAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Program, ProgramAdmin)
admin.site.register(Navigator, NavigatorAdmin)
admin.site.register(UrgentNeed, UrgentNeedAdmin)
admin.site.register(UrgentNeedFunction, UrgentNeedsFunctionAdmin)
admin.site.register(FederalPoveryLimit, FederalPovertyLimitAdmin)
admin.site.register(Referrer, ReferrerAdmin)
admin.site.register(WebHookFunction, WebHookFunctionsAdmin)
