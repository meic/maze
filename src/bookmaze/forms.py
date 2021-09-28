from django.contrib.auth import forms as auth_forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Layout, Submit

from crispy_bootstrap5.bootstrap5 import FloatingField


class AuthenticationForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-login"
        self.helper.layout = Layout(
            FloatingField("username"),
            FloatingField("password"),
            ButtonHolder(Submit("submit", "Login", css_class="w-100 btn-lg")),
        )


class UserCreationForm(auth_forms.UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Add User"))
