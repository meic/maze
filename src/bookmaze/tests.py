from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from bookmaze.forms import AuthenticationForm, UserCreationForm


class BookmazeFormsTest(TestCase):
    def test_authentication_form_layout(self):
        form = AuthenticationForm()
        self.assertEqual(form.helper.form_method, "post")
        self.assertEqual(form.helper.form_class, "form-login")
        html = form.as_p()
        self.assertIn("username", html)
        self.assertIn("password", html)

    def test_user_creation_form_layout(self):
        form = UserCreationForm()
        self.assertEqual(form.helper.form_method, "post")
        html = form.as_p()
        self.assertIn("username", html)


class BookmazeViewsTest(TestCase):
    def setUp(self):
        # Create users
        self.password = "Secr3tP@ssword"
        self.user = User.objects.create_user(username="normaluser", password=self.password)
        
        # User with user management permissions
        self.admin_user = User.objects.create_user(username="adminuser", password=self.password)
        content_type = ContentType.objects.get_for_model(User)
        add_perm = Permission.objects.get(codename="add_user", content_type=content_type)
        view_perm = Permission.objects.get(codename="view_user", content_type=content_type)
        self.admin_user.user_permissions.add(add_perm, view_perm)
        
        # Superuser
        self.superuser = User.objects.create_superuser(username="superuser", password=self.password)

    def test_login_view_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/login.html")

    def test_login_view_post_success(self):
        post_data = {
            "username": "normaluser",
            "password": self.password,
        }
        response = self.client.post(reverse("login"), data=post_data)
        # Redirects to LOGIN_REDIRECT_URL, which is "/"
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_failure(self):
        post_data = {
            "username": "normaluser",
            "password": "WrongPassword",
        }
        response = self.client.post(reverse("login"), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/login.html")
        self.assertFalse(response.context["form"].is_valid())

    def test_logout_view(self):
        self.client.login(username="normaluser", password=self.password)
        # Perform logout (LogoutView supports POST)
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/logout.html")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_create_view_anonymous_redirect(self):
        response = self.client.get(reverse("user_create"))
        # PermissionRequiredMixin redirects anonymous user to login
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('user_create')}")

    def test_user_create_view_unauthorized(self):
        self.client.login(username="normaluser", password=self.password)
        response = self.client.get(reverse("user_create"))
        # Lacks auth.add_user permission, returns 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_user_create_view_authorized_get(self):
        self.client.login(username="adminuser", password=self.password)
        response = self.client.get(reverse("user_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/form_view.html")
        self.assertEqual(response.context["title"], "Add User")

    def test_user_create_view_authorized_post_success(self):
        self.client.login(username="adminuser", password=self.password)
        post_data = {
            "username": "newlycreateduser",
            "password1": "SecureNewPass123!",
            "password2": "SecureNewPass123!",
        }
        response = self.client.post(reverse("user_create"), data=post_data)
        self.assertRedirects(response, reverse("user_list"))
        self.assertTrue(User.objects.filter(username="newlycreateduser").exists())

    def test_user_list_view_anonymous_redirect(self):
        response = self.client.get(reverse("user_list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('user_list')}")

    def test_user_list_view_unauthorized(self):
        self.client.login(username="normaluser", password=self.password)
        response = self.client.get(reverse("user_list"))
        # Lacks auth.view_user permission, returns 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_user_list_view_authorized(self):
        self.client.login(username="adminuser", password=self.password)
        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookmaze/user_list.html")
        
        # Verify it lists users
        user_list = response.context["user_list"]
        self.assertIn(self.user, user_list)
        self.assertIn(self.admin_user, user_list)
        
        # Excludes superusers
        self.assertNotIn(self.superuser, user_list)
