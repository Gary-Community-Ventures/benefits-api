from django.urls import path
from . import views


urlpatterns = [
    path('', views.TranslationView.as_view())
]
