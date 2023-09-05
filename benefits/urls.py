"""benefits URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from sesame.views import LoginView

urlpatterns = [
    path('api/', include('screener.urls')),
    path('api/', include('programs.urls')),
    path('api/', include('authentication.urls')),
    path('translations/', include('translations.urls')),
    path('admin/', admin.site.urls),
    path("sesame/login/", LoginView.as_view(), name="sesame-login"),
    path('openapi', get_schema_view(
        title="Colorado Open Benefits API",
        description="API calculates eligibility across over 40 benefit programs in Colorado",
        version="0.0.1",
        public=True,
        permission_classes=[],
        authentication_classes=[]
    ), name='openapi-schema'),
    path('api/documentation/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui')
]
