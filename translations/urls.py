from django.urls import path
from . import views


urlpatterns = [
    path("", views.TranslationView.as_view()),
    path("admin", views.admin_view, name="translations_api_url"),
    path("admin/filter", views.filter_view),
    path("admin/create", views.create_translation_view),
    path("admin/programs", views.programs_view),
    path("admin/programs/filter", views.programs_filter_view),
    path("admin/programs/create", views.create_program_view),
    path("admin/programs/<int:id>", views.program_view),
    path("admin/navigators", views.navigators_view),
    path("admin/navigators/filter", views.navigator_filter_view),
    path("admin/navigators/create", views.create_navigator_view),
    path("admin/navigators/<int:id>", views.navigator_view),
    path("admin/documents", views.documents_view),
    path("admin/documents/filter", views.document_filter_view),
    path("admin/documents/create", views.create_document_view),
    path("admin/documents/<int:id>", views.document_view),
    path("admin/urgent_needs", views.urgent_needs_view),
    path("admin/urgent_needs/filter", views.urgent_need_filter_view),
    path("admin/urgent_needs/create", views.create_urgent_need_view),
    path("admin/urgent_needs/<int:id>", views.urgent_need_view),
    path("admin/<int:id>", views.translation_view, name="translation_admin_url"),
    path("admin/<int:id>/<str:lang>", views.edit_translation),
    path("admin/<int:id>/<str:lang>/auto", views.auto_translate),
]
