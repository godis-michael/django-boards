from django.core import mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from boards.tests.utils import create_response


class PasswordResetMailTests(TestCase):
    def setUp(self):
        email_address = 'test@mail.com'
        User.objects.create_user(username='john', email=email_address, password='test12345')
        self.response = create_response(client=self.client.post, url='accounts:password_reset', data={'email': email_address})
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEquals(self.email.subject, '[Django Boards] Password reset confirmation')

    def test_email_body(self):
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('john', self.email.body)
        self.assertIn('test@mail.com', self.email.body)