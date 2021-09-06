from django.contrib.auth import views as auth_views

from .forms import AuthenticationForm


class LoginView(auth_views.LoginView):
    authentication_form = AuthenticationForm
    template_name = "bookmaze/login.html"


class LogoutView(auth_views.LogoutView):
    template_name = "bookmaze/logout.html"
