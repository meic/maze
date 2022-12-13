from django import forms

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    validate_password,
    password_validators_help_text_html,
)

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.forms import ValidationError

from .models import AccessCode


class CreateAccountForm(forms.Form):
    access_code = forms.CharField(required=True)
    username = forms.CharField(required=True)
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        help_text=password_validators_help_text_html,
    )
    password_confirm = forms.CharField(
        label="Confirm password", required=True, widget=forms.PasswordInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Create"))

    def clean_access_code(self):
        data = self.cleaned_data["access_code"]
        try:
            acccess_code = AccessCode.objects.get(access_code=data)
            return acccess_code
        except AccessCode.DoesNotExist:
            raise ValidationError("Incorrect access code", code="incorrect-access-code")

    def clean_username(self):
        data = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=data).exists():
            raise ValidationError("User already exists", code="user-exists")
        return data

    def clean_password(self):
        data = self.cleaned_data["password"]
        validate_password(data)
        return data

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password != password_confirm:
            msg = "Passwords didn't match"
            self.add_error("password", msg)
            self.add_error("password_confirm", msg)

    def create_user(self, request=None):
        user = User.objects.create_user(
            self.cleaned_data["username"], password=self.cleaned_data["password"]
        )
        self.cleaned_data["access_code"].users.add(user)
        if request:
            login(request, user)
        return user
