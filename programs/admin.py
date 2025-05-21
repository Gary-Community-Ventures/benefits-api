from django.contrib import admin
from django.db.models import Q
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


# WARNING: This is only for the user experience. This does not prevent admin from
# using the API to edit programs they don't have access to
class WhiteLabelModelAdminMixin(ModelAdmin):
    white_label_filter_horizontal = []

    # dont list white labels the admin does not have access to
    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)

        # limit the white labels shown based on the admin permisions
        return super().get_queryset(request).filter(white_label__in=request.user.white_labels.all())

    # limit the objects the user can select to
    # the objects with the same white label as the object the admin is editing
    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        user_white_labels = request.user.white_labels.all()

        white_label_input = context["adminform"].form.fields["white_label"]
        original_white_label_queryset = white_label_input.queryset
        white_label_input.queryset = white_label_input.queryset.filter(id__in=user_white_labels)

        if obj is None:
            return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)

        for field in self.white_label_filter_horizontal:
            form_field = context["adminform"].form.fields[field]
            restricted_query_set = form_field.queryset.filter(
                Q(white_label=obj.white_label) | Q(id__in=getattr(obj, field).all().values_list("id", flat=True))
            )
            if not request.user.is_superuser:
                restricted_query_set = restricted_query_set.filter(white_label__in=user_white_labels)

            form_field.queryset = restricted_query_set

        if request.user.is_superuser:
            white_label_input.queryset = original_white_label_queryset
            return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)

        return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)


class ProgramAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("name__translations__text",)
    list_display = ["get_str", "name_abbreviated", "active", "action_buttons"]
    white_label_filter_horizontal = [
        "documents",
        "required_programs",
    ]
    filter_horizontal = (
        "legal_status_required",
        "documents",
        "required_programs",
    )
    exclude = [
        "name",
        "description",
        "description_short",
        "learn_more_link",
        "apply_button_link",
        "apply_button_description",
        "estimated_delivery_time",
        "estimated_application_time",
        "value_type",
        "website_description",
        "estimated_value",
    ]

    def has_add_permission(self, request):
        return False

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
        apply_button_description = obj.apply_button_description
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
                    <a href="{}">Apply Button Description</a>
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
            reverse("translation_admin_url", args=[apply_button_description.id]),
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


class CountiesAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("name",)


class NavigatorLanguageAdmin(ModelAdmin):
    search_fields = ("code",)


class NavigatorAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("name__translations__text",)
    list_display = ["get_str", "external_name", "action_buttons"]
    white_label_filter_horizontal = ("programs", "counties")
    filter_horizontal = ("programs", "counties", "languages")
    exclude = [
        "name",
        "email",
        "assistance_link",
        "description",
    ]

    def has_add_permission(self, request):
        return False

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


class WarningMessageAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "calculator", "action_buttons"]
    white_label_filter_horizontal = (
        "programs",
        "counties",
    )
    filter_horizontal = (
        "programs",
        "counties",
        "legal_statuses",
    )
    exclude = ["message"]

    def has_add_permission(self, request):
        return False

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
                    <a href="{}">Warning Message</a>
                    <a href="{}">Warning Message Link</a>
                    <a href="{}">Warning Message Link Text</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[obj.message.id]),
            reverse("translation_admin_url", args=[obj.link_url.id]),
            reverse("translation_admin_url", args=[obj.link_text.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class UrgentNeedAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("name__translations__text",)
    list_display = ["get_str", "external_name", "active", "action_buttons"]
    white_label_filter_horizontal = ("counties",)
    filter_horizontal = (
        "type_short",
        "functions",
        "counties",
    )
    exclude = [
        "name",
        "description",
        "link",
        "type",
        "warning",
        "website_description",
    ]

    def has_add_permission(self, request):
        return False

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


class DocumentAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "action_buttons"]
    exclude = ["text", "link_url", "link_text"]

    def has_add_permission(self, request):
        return False

    def get_str(self, obj):
        return str(obj)

    get_str.admin_order_field = "external_name"
    get_str.short_description = "Document"

    def action_buttons(self, obj):

        return format_html(
            """
            <div class="dropdown">
                <span class="dropdown-btn material-symbols-outlined"> menu </span>
                <div class="dropdown-content">
                    <a href="{}">Text</a>
                    <a href="{}">Link Url</a>
                    <a href="{}">Link Text</a>
                </div>
            </div>
            """,
            reverse("translation_admin_url", args=[obj.text.id]),
            reverse("translation_admin_url", args=[obj.link_url.id]),
            reverse("translation_admin_url", args=[obj.link_text.id]),
        )

    action_buttons.short_description = "Translate:"
    action_buttons.allow_tags = True


class ReferrerAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("referrer_code",)
    white_label_filter_horizontal = (
        "primary_navigators",
        "remove_programs",
    )
    filter_horizontal = (
        "webhook_functions",
        "primary_navigators",
        "remove_programs",
    )


class WebHookFunctionsAdmin(ModelAdmin):
    search_fields = ("name",)


class TranslationOverrideAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "calculator", "action_buttons"]
    white_label_filter_horizontal = ("counties",)
    filter_horizontal = ("counties",)
    exclude = ["translation"]

    def has_add_permission(self, request):
        return False

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


class ProgramCategoryAdmin(WhiteLabelModelAdminMixin, ModelAdmin):
    search_fields = ("external_name",)
    list_display = ["get_str", "external_name", "action_buttons"]
    exclude = ["name", "description"]

    def has_add_permission(self, request):
        return False

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
