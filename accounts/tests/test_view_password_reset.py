from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.core import mail
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from boards.tests.utils import create_response


class PasswordResetTests(TestCase):
    def setUp(self):
        self.response = create_response(client=self.client.get, url='accounts:password_reset')

    def test_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/reset/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_view_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        email = 'john@mail.com'
        User.objects.create_user(username='john', email=email, password='test12345')
        self.response = create_response(client=self.client.post, url='accounts:password_reset', data={'email': email})

    def test_view_redirection(self):
        """
            A valid form submission should redirect the user to `password_reset_done` view
        """
        url = reverse('accounts:password_reset_done')
        self.assertRedirects(self.response, url)

    def test_reset_password_mail_is_sent(self):
        self.assertEquals(len(mail.outbox), 1)


class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        self.response = create_response(client=self.client.post, url='accounts:password_reset', data={'email': 'doesnotexist@mail.com'})

    def test_view_redirection(self):
        url = reverse('accounts:password_reset_done')
        self.assertRedirects(self.response, url)

    def test_reset_password_mail_not_sent(self):
        self.assertEquals(len(mail.outbox), 0)


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        self.response = create_response(client=self.client.get, url='accounts:password_reset_done')

    def test_password_reset_done_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_password_reset_done_url_resolves_correct_view(self):
        view = resolve('/reset/done/')
        self.assertEquals(auth_views.PasswordResetDoneView, view.func.view_class)


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        email = 'john@mail.com'
        user = User.objects.create_user(username='john', email=email, password='test12345')
        self.uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        self.token = default_token_generator.make_token(user)
        url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(url, follow=True)

    def test_password_reset_confirm_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_password_reset_confirm_url_resolves_correct_view(self):
        view = resolve('/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
        self.assertEquals(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_password_reset_confirm_view_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)

    def test_password_reset_confirm_view_inputs(self):
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        email = 'john@mail.com'
        user = User.objects.create_user(username='john', email=email, password='test12345')
        uid = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)

        user.set_password('newpass12345')
        user.save()

        url = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.response = self.client.get(url)

    def test_password_reset_confirm_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_password_reset_confirm_html(self):
        url = reverse('accounts:password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(self.response, 'href="{url_back}'.format(url_back=url))

class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        self.response = create_response(client=self.client.get, url='accounts:password_reset_complete')

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/complete/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)