from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from api import views

api_endpoints = [
    path(name, view)
    for name, view in views.generate_endpoints().items()
]

api_info = openapi.Info(
    title="Galaxy API",
    default_version='v1',
    license=openapi.License(name="GNU General Public License v3.0"),
)

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=api_endpoints
)

urlpatterns = [
    path('', schema_view.with_ui('swagger'))
]

urlpatterns += api_endpoints
