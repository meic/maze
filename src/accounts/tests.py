from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.forms import ValidationError
from django.urls import reverse

from accounts.models import AccessCode
from accounts.forms import CreateAccountForm


class AccessCodeModelTest(TestCase):
    def test_access_code_creation(self):
        ac = AccessCode.objects.create(access_code="TESTCODE")
        self.assertEqual(ac.access_code, "TESTCODE")
        self.assertEqual(ac.users.count(), 0)
        self.assertEqual(str(ac.access_code), "TESTCODE")

    def test_access_code_uniqueness(self):
        AccessCode.objects.create(access_code="TESTCODE")
        with self.assertRaises(IntegrityError):
            AccessCode.objects.create(access_code="TESTCODE")


class CreateAccountFormTest(TestCase):
    def setUp(self):
        self.access_code = AccessCode.objects.create(access_code="VALIDCODE")
        self.existing_user = User.objects.create_user(username="existing", password="password123")

    def test_valid_form(self):
        form_data = {
            "access_code": "VALIDCODE",
            "username": "newuser",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
        }
        form = CreateAccountForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors.as_data())

        # Test user creation
        user = form.create_user()
        self.assertEqual(user.username, "newuser")
        self.assertTrue(user.check_password("ValidPassword123!"))
        self.assertTrue(self.access_code.users.filter(username="newuser").exists())

    def test_invalid_access_code(self):
        form_data = {
            "access_code": "INVALIDCODE",
            "username": "newuser",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
        }
        form = CreateAccountForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("access_code", form.errors)
        self.assertEqual(form.errors.as_data()["access_code"][0].code, "incorrect-access-code")

    def test_username_exists(self):
        form_data = {
            "access_code": "VALIDCODE",
            "username": "existing",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
        }
        form = CreateAccountForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(form.errors.as_data()["username"][0].code, "user-exists")

    def test_username_exists_case_insensitive(self):
        form_data = {
            "access_code": "VALIDCODE",
            "username": "ExIsTiNg",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
        }
        form = CreateAccountForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(form.errors.as_data()["username"][0].code, "user-exists")

    def test_password_validation_failure(self):
        # Extremely short password
        form_data = {
            "access_code": "VALIDCODE",
            "username": "newuser",
            "password": "123",
            "password_confirm": "123",
        }
        form = CreateAccountForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)

    def test_password_mismatch(self):
        form_data = {
            "access_code": "VALIDCODE",
            "username": "newuser",
            "password": "ValidPassword123!",
            "password_confirm": "DifferentPassword123!",
        }
        form = CreateAccountForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
        self.assertIn("password_confirm", form.errors)


class CreateAccountViewTest(TestCase):
    def setUp(self):
        self.access_code = AccessCode.objects.create(access_code="VALIDCODE")

    def test_get_create_account(self):
        response = self.client.get(reverse("accounts:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/form_view.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], CreateAccountForm)
        self.assertEqual(response.context["title"], "Create Account")

    def test_post_create_account_success(self):
        post_data = {
            "access_code": "VALIDCODE",
            "username": "newuser",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
        }
        response = self.client.post(reverse("accounts:create"), data=post_data)
        self.assertRedirects(response, reverse("maze:index"))

        # Verify user is created and logged in
        user = User.objects.get(username="newuser")
        self.assertTrue(user.is_authenticated)
        self.assertTrue(self.access_code.users.filter(username="newuser").exists())

    def test_post_create_account_failure(self):
        post_data = {
            "access_code": "INVALIDCODE",
            "username": "newuser",
            "password": "ValidPassword123!",
            "password_confirm": "ValidPassword123!",
        }
        response = self.client.post(reverse("accounts:create"), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/form_view.html")
        self.assertFalse(response.context["form"].is_valid())
