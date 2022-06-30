from django.urls import include, path
from rest_framework import routers
from screener import views

from . import views

router = routers.DefaultRouter()
router.register(r'screens', views.ScreenViewSet)
router.register(r'incomestreams', views.IncomeStreamViewSet)
router.register(r'expenses', views.ExpenseViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('eligibility/<int:id>', views.EligibilityView.as_view(), name='screen eligibility endpoint')
]
