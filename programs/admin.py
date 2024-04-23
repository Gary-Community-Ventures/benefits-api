from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
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


class ProgramAdmin(ModelAdmin):
    search_fields = ("name_abbreviated",)
    list_display = ["get_str", "name_abbreviated", "action_buttons"]

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "name"
    get_str.short_description = "Program"

    def action_buttons(self, obj):
        name = obj.name
        description = obj.description
        description_short = obj.description_short
        learn_more_link = obj.learn_more_link
        apply_button_link = obj.apply_button_link
        category = obj.category
        estimated_delivery_time = obj.estimated_delivery_time
        estimated_application_time = obj.estimated_application_time
        value_type = obj.value_type
        warning = obj.warning

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Name</a>
                    <a href="{}">Description</a>
                    <a href="{}">Short Description</a>
                    <a href="{}">Category</a>
                    <a href="{}">Learn More Link</a>
                    <a href="{}">Apply Button Link</a>
                    <a href="{}">Estimated Delivery Time</a>
                    <a href="{}">Estimated Application Time</a>
                    <a href="{}">Value Type</a>
                    <a href="{}">Warning</a>
                </div>
            </div>
        """,
            reverse("translation_admin_url", args=[name.id]),
            reverse("translation_admin_url", args=[description.id]),
            reverse("translation_admin_url", args=[description_short.id]),
            reverse("translation_admin_url", args=[category.id]),
            reverse("translation_admin_url", args=[learn_more_link.id]),
            reverse("translation_admin_url", args=[apply_button_link.id]),
            reverse("translation_admin_url", args=[
                    estimated_delivery_time.id]),
            reverse("translation_admin_url", args=[
                    estimated_application_time.id]),
            reverse("translation_admin_url", args=[value_type.id]),
            reverse("translation_admin_url", args=[warning.id]),
        )

    action_buttons.short_description = "Translate"
    action_buttons.allow_tags = True


class LegalStatusAdmin(ModelAdmin):
    search_fields = ("status",)


class NavigatorCountiesAdmin(ModelAdmin):
    search_fields = ("name",)


class NavigatorAdmin(ModelAdmin):
    search_fields = ("translations__name",)
    list_display = ["get_str", "external_name", "get_name_link"]
    readonly_fields = ("get_name_link",)

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "name"
    get_str.short_description = "Navigator"

    def get_name_link(self, obj):
        translation = obj.name
        url = reverse("admin:translations_translation_change",
                      args=(translation.id,))
        return format_html('<a href="{}">{}</a>', url, translation)

    get_name_link.admin_order_field = "name"
    get_name_link.short_description = "Label"


class UrgentNeedAdmin(ModelAdmin):
    search_fields = ("translations__name",)
    list_display = ["__str__", "external_name", "active", "get_name_link"]

    def get_name_link(self, obj):
        translation = obj.name
        url = reverse("admin:translations_translation_change",
                      args=(translation.id,))
        return format_html('<a href="{}">{}</a>', url, translation)

    get_name_link.admin_order_field = "name"
    get_name_link.short_description = "Label"


class UrgentNeedCategoryAdmin(ModelAdmin):
    search_fields = ("name",)
    fields = ("name",)


class UrgentNeedFunctionAdmin(ModelAdmin):
    search_fields = ("name",)
    fields = ("name",)


class FederalPovertyLimitAdmin(ModelAdmin):
    search_fields = ("year",)


class DocumentAdmin(ModelAdmin):
    search_fields = ("name",)


class ReferrerAdmin(ModelAdmin):
    search_fields = ("referrer_code",)


class WebHookFunctionsAdmin(ModelAdmin):
    search_fields = ("name",)


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
