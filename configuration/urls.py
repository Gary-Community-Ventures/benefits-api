from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"configuration/(?P<white_label>.+)", views.ConfigurationView, basename="Configuration")

urlpatterns = [
    path("", include(router.urls)),
]
