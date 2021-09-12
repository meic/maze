from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.list import ListView

from .forms import AuthenticationForm


class LoginView(auth_views.LoginView):
    authentication_form = AuthenticationForm
    template_name = "bookmaze/login.html"


class LogoutView(auth_views.LogoutView):
    template_name = "bookmaze/logout.html"


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = ("auth.view_user",)
    template_name = "bookmaze/user_list.html"
    model = User
