from django.contrib.auth.views import LoginView as AuthLoginView

from .forms import AuthenticationForm


class LoginView(AuthLoginView):
    authentication_form = AuthenticationForm
    template_name = "bookmaze/login.html"
