from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("create", views.CreateAccountView.as_view(), name="create"),
]
