from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from .forms import AuthenticationForm, UserCreationForm


class LoginView(auth_views.LoginView):
    authentication_form = AuthenticationForm
    template_name = "bookmaze/login.html"


class LogoutView(auth_views.LogoutView):
    template_name = "bookmaze/logout.html"


class UserCreateView(PermissionRequiredMixin, CreateView):
    extra_context = {"title": "Add User"}
    permission_required = ("auth.add_user",)
    template_name = "bookmaze/form_view.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("user_list")


class UserListView(PermissionRequiredMixin, ListView):
    permission_required = ("auth.view_user",)
    template_name = "bookmaze/user_list.html"
    model = User
