from django.urls import path, re_path

from api import views
from api import swagger

urlpatterns = [
    re_path(r'^(?P<type>json|xml)/(?P<endpoint>[\w-]+)/$', views.DispatchView.as_view()),
    path('manage/load-descriptions/', views.ManageLoadView.as_view()),
    path('swagger/', swagger.schema_view)
]
