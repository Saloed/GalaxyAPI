from django.urls import path, re_path

from api import views

urlpatterns = [
    re_path(r'^(?P<type>json|xml)/(?P<endpoint>[\w-]+)/$', views.DispatchView.as_view())
]
