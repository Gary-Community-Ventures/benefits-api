from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from .models import (
    LegalStatus,
    Program,
    ProgramCategory,
    UrgentNeed,
    Navigator,
    UrgentNeedFunction,
    FederalPoveryLimit,
    Referrer,
    WarningMessage,
    WebHookFunction,
    UrgentNeedCategory,
    County,
    NavigatorLanguage,
    Document,
    TranslationOverride,
)


class ProgramAdmin(ModelAdmin):
    search_fields = ("name__translations__text",)
    list_display = ["get_str", "name_abbreviated", "active", "action_buttons"]
    filter_horizontal = (
        "legal_status_required",
        "documents",
    )

    def get_str(self, obj):
        return str(obj) if str(obj).strip() else "unnamed"

    get_str.admin_order_field = "name"
    get_str.short_description = "Program"

    def action_buttons(self, obj):
        name = obj.name
        description = obj.description
        description_short = obj.description_short
        learn_more_link = obj.learn_more_link
        apply_button_link = obj.apply_button_link
        estimated_delivery_time = obj.estimated_delivery_time
        estimated_application_time = obj.estimated_application_time
        value_type = obj.value_type
        website_description = obj.website_description
        estimated_value = obj.estimated_value

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Name</a>
                    <a href="{}">Description</a>
                    <a href="{}">Short Description</a>
                    <a href="{}">Learn More Link</a>
                    <a href="{}">Apply Button Link</a>
                    <a href="{}">Estimated Delivery Time</a>
                    <a href="{}">Estimated Application Time</a>
                    <a href="{}">Value Type</a>
                    <a href="{}">Website Description</a>
                    <a href="{}">Estimated Value</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[name.id]),
            reverse("translation_admin_url", args=[description.id]),
            reverse("translation_admin_url", args=[description_short.id]),
            reverse("translation_admin_url", args=[learn_more_link.id]),
            reverse("translation_admin_url", args=[apply_button_link.id]),
            reverse("translation_admin_url", args=[estimated_delivery_time.id]),
            reverse("translation_admin_url", args=[estimated_application_time.id]),
            reverse("translation_admin_url", args=[value_type.id]),
            reverse("translation_admin_url", args=[website_description.id]),
            reverse("translation_admin_url", args=[estimated_value.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class LegalStatusAdmin(ModelAdmin):
    search_fields = ("status",)


class CountiesAdmin(ModelAdmin):
    search_fields = ("name",)


class NavigatorLanguageAdmin(ModelAdmin):
    search_fields = ("code",)


class NavigatorAdmin(ModelAdmin):
    search_fields = ("name__translations__text",)
    list_display = ["get_str", "external_name", "action_buttons"]
    filter_horizontal = ("programs", "counties", "languages")

    def get_str(self, obj):
        return str(obj) if str(obj).strip() else "unnamed"

    get_str.admin_order_field = "name"
    get_str.short_description = "Navigator"

    def action_buttons(self, obj):
        name = obj.name
        email = obj.email
        assistance_link = obj.assistance_link
        description = obj.description

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Name</a>
                    <a href="{}">Email</a>
                    <a href="{}">Assistance Link</a>
                    <a href="{}">Description</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[name.id]),
            reverse("translation_admin_url", args=[email.id]),
            reverse("translation_admin_url", args=[assistance_link.id]),
            reverse("translation_admin_url", args=[description.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class WarningMessageAdmin(ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "calculator", "action_buttons"]
    filter_horizontal = (
        "programs",
        "counties",
    )

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "external_name"
    get_str.short_description = "Name"

    def action_buttons(self, obj):
        message = obj.message

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Warning message</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[message.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class UrgentNeedAdmin(ModelAdmin):
    search_fields = ("name__translations__text",)
    list_display = ["get_str", "external_name", "active", "action_buttons"]
    filter_horizontal = (
        "type_short",
        "functions",
    )

    def get_str(self, obj):
        return str(obj) if str(obj).strip() else "unnamed"

    get_str.admin_order_field = "name"
    get_str.short_description = "Urgent Need"

    def action_buttons(self, obj):
        name = obj.name
        description = obj.description
        link = obj.link
        type = obj.type
        warning = obj.warning
        website_description = obj.website_description

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Name</a>
                    <a href="{}">Description</a>
                    <a href="{}">Link</a>
                    <a href="{}">Type</a>
                    <a href="{}">Warning</a>
                    <a href="{}">Website Description</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[name.id]),
            reverse("translation_admin_url", args=[description.id]),
            reverse("translation_admin_url", args=[link.id]),
            reverse("translation_admin_url", args=[type.id]),
            reverse("translation_admin_url", args=[warning.id]),
            reverse("translation_admin_url", args=[website_description.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class UrgentNeedCategoryAdmin(ModelAdmin):
    search_fields = ("name",)
    fields = ("name",)


class UrgentNeedFunctionAdmin(ModelAdmin):
    search_fields = ("name",)
    fields = ("name",)


class FederalPovertyLimitAdmin(ModelAdmin):
    search_fields = ("year",)


class DocumentAdmin(ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "action_buttons"]

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "external_name"
    get_str.short_description = "Document"

    def action_buttons(self, obj):
        text = obj.text

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Document Text</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[text.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class ReferrerAdmin(ModelAdmin):
    search_fields = ("referrer_code",)
    filter_horizontal = (
        "webhook_functions",
        "primary_navigators",
        "remove_programs",
    )


class WebHookFunctionsAdmin(ModelAdmin):
    search_fields = ("name",)


class TranslationOverrideAdmin(ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "calculator", "action_buttons"]
    filter_horizontal = ("counties",)

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "external_name"
    get_str.short_description = "Name"

    def action_buttons(self, obj):
        message = obj.translation

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Translation Override</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[message.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class ProgramCategoryAdmin(ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "external_name", "action_buttons"]

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "external_name"
    get_str.short_description = "Name"

    def action_buttons(self, obj):
        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Name</a>
                    <a href="{}">Description</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[obj.name.id]),
            reverse("translation_admin_url", args=[obj.description.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


admin.site.register(LegalStatus, LegalStatusAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(County, CountiesAdmin)
admin.site.register(NavigatorLanguage, NavigatorLanguageAdmin)
admin.site.register(Navigator, NavigatorAdmin)
admin.site.register(WarningMessage, WarningMessageAdmin)
admin.site.register(UrgentNeed, UrgentNeedAdmin)
admin.site.register(UrgentNeedCategory, UrgentNeedCategoryAdmin)
admin.site.register(UrgentNeedFunction, UrgentNeedFunctionAdmin)
admin.site.register(FederalPoveryLimit, FederalPovertyLimitAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Referrer, ReferrerAdmin)
admin.site.register(WebHookFunction, WebHookFunctionsAdmin)
admin.site.register(TranslationOverride, TranslationOverrideAdmin)
admin.site.register(ProgramCategory, ProgramCategoryAdmin)
