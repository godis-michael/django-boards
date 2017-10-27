from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from boards.tests.utils import create_response


class PasswordChangeTests(TestCase):
    def setUp(self):
        username = 'john'
        email = 'john@mail.com'
        password = 'test12345'
        user = User.objects.create_user(username=username, email=email, password=password)
        self.client.login(username=username, password=password)
        self.response = create_response(client=self.client.get, url='accounts:password_change')

    def test_password_change_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_password_change_url_resolves_correct_view(self):
        view = resolve('/settings/password/')
        self.assertEquals(view.func.view_class, auth_views.PasswordChangeView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_password_change_view_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)

    def test_password_change_view_contains_correct_inputs(self):
        """
            Should contain 4 inputs: csrf, old pass, new pass, confirm new pass
        """
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="password"', 3)


class LoginRequiredPasswordChangeTests(TestCase):
    def test_password_change_redirection_user_not_logged_in(self):
        url = reverse('accounts:password_change')
        login_url = reverse('accounts:login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')


class PasswordChangeTestCase(TestCase):
    def setUp(self, data=None):
        if data is None:
            data = {}
        username = 'john'
        email = 'john@mail.com'
        password = 'old_password'
        self.user = User.objects.create_user(username=username, email=email, password=password)
        self.url = reverse('accounts:password_change')
        self.client.login(username=username, password=password)
        self.response = self.client.post(self.url, data)


class SuccessfulPassworChangeTests(PasswordChangeTestCase):
    def setUp(self, data=None):
        super().setUp({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password'
        })

    def test_successful_password_change_view_redirects_to_password_change_done_page(self):
        self.assertRedirects(self.response, reverse('accounts:password_change_done'))

    def test_successful_password_change_view_password_changed(self):
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_successful_password_change_view_user_authenticated(self):
        response = create_response(client=self.client.get, url='boards:home')
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase):
    def invalid_password_change_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def invalid_password_change_view_has_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def invalid_password_change_view_didnt_change_password(self):
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))