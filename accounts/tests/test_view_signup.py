from django.test import TestCase
from django.urls import resolve
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from boards.tests.test_view import create_response
from ..views import signup
from ..forms import SignUpForm


class SignUpTests(TestCase):
    def setUp(self):
        self.response = create_response(client=self.client.get, url='accounts:signup')

    def test_signup_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_signup_view_contains_signup_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_signup_form_contains_right_inputs(self):
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        data = {
            'username': 'john',
            'email': 'john@mail.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = create_response(client=self.client.post, url='accounts:signup', data=data)
        self.home_url = reverse('boards:home')

    def test_signup_view_redirects_to_homepage(self):
        """
            A valid form submission should redirect the user to the home page
        """
        self.assertRedirects(self.response, self.home_url)

    def test_signup_view_creates_new_user(self):
        self.assertTrue(User.objects.exists())

    def test_user_is_authenticated_after_signup(self):
        """
            Create a new request to an arbitrary page.
            The resulting response should now have an `user` to its context,
            after a successful sign up.
        """
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUTests(TestCase):
    def setUp(self):
        self.response = create_response(client=self.client.post, url='accounts:signup', data={})

    def test_signup_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_view_errors_exist(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_signup_view_doesnt_create_any_user(self):
        self.assertFalse(User.objects.exists())

