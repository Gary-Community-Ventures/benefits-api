from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"programs", views.ProgramViewSet)
router.register(r"program_categories", views.ProgramCategoryViewSet)
router.register(r"navigators", views.NavigatorViewSet)
router.register(r"urgent-needs", views.UrgentNeedViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [path("", include(router.urls))]
