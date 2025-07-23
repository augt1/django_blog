from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.set_timezone, name="set_timezone"),
]