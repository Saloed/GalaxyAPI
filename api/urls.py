from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from api import views

api_endpoints = [
    path(name, view)
    for name, view in views.generate_endpoints().items()
]

schema_view = get_swagger_view('Api swagger schema', url='/api', patterns=api_endpoints)

urlpatterns = [
    path('manage/load-descriptions/', views.ManageLoadView.as_view()),
    path('', schema_view)
]

urlpatterns += api_endpoints
