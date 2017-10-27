from django.test import TestCase
from django.urls import reverse
from .utils import create_response
from ..models import Board


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django Board.')
        self.url = reverse('boards:new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('accounts:login')
        self.assertRedirects(self.response, f'{login_url}?next={self.url}')