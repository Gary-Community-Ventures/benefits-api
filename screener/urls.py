from django.urls import include, path
from rest_framework import routers
from screener import views

from . import views

router = routers.DefaultRouter()
router.register(r'screens', views.ScreenViewSet)
router.register(r'incomestreams', views.IncomeStreamViewSet)
router.register(r'expenses', views.ExpenseViewSet)
# router.register(r'(?P<client_id>\d+)/requests', views.EligibilityView.as_view(), basename='screen eligibility endpoint')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/eligibility/<int:id>', views.EligibilityView.as_view(), name='screen eligibility endpoint')
]
