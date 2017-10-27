from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth import login

from .utils import create_response
from ..views import BoardListView, TopicListView, new_topic
from ..models import Board, Topic, Post
from ..forms import NewTopicForm


class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.response = create_response(client=self.client.get, url='boards:home')

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_vies(self):
        view = resolve('/')
        self.assertEquals(view.func.view_class, BoardListView)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('boards:board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))


class BoardTopicsTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.valid_get_response = create_response(client=self.client.get, url='boards:board_topics', pk=self.board.pk)
        self.invalid_get_response = create_response(client=self.client.get, url='boards:board_topics', pk=99)

    def test_board_topics_view_success_status_code(self):
        self.assertEquals(self.valid_get_response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        self.assertEquals(self.invalid_get_response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/{0}/'.format(self.board.pk))
        self.assertEquals(view.func.view_class, TopicListView)

    def test_boar_topics_view_contains_navigation_links(self):
        homepage_url = reverse('boards:home')
        new_topic_url = reverse('boards:new_topic', kwargs={'pk': self.board.pk})
        self.assertContains(self.valid_get_response, 'href="{0}"'.format(homepage_url))
        self.assertContains(self.valid_get_response, 'href="{0}"'.format(new_topic_url))


class NewTopicTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Dajngo Board.')
        self.user = User.objects.create_user(username='john', email='john@mail.com', password='test123')
        self.client.login(username='john', password='test123')

        self.valid_get_response = create_response(client=self.client.get, url='boards:new_topic', pk=self.board.pk)
        self.invalid_get_response = create_response(client=self.client.get, url='boards:new_topic', pk=99)

    def test_csrf(self):
        self.assertContains(self.valid_get_response, 'csrfmiddlewaretoken')

    def test_new_topic_view_success_status_code(self):
        self.assertEquals(self.valid_get_response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        self.assertEquals(self.invalid_get_response.status_code, 404)

    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/{0}/new/'.format(self.board.pk))
        self.assertEquals(view.func, new_topic)

    def test_new_topic_view_contains_navigation_links(self):
        homepage_url = reverse('boards:home')
        board_topics_url = reverse('boards:board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.valid_get_response, 'href="{0}"'.format(homepage_url))
        self.assertContains(self.valid_get_response, 'href="{0}"'.format(board_topics_url))

    def test_new_topic_valid_post_data(self):
        data = {'subject': 'Test',
                'message': 'Test message.'}
        valid_post_response = create_response(client=self.client.post, url='boards:new_topic', data=data, pk=self.board.pk)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        """
            Invalid post data should not redirect
            The expected behavior is to show the form again with validation errors
        """
        invalid_post_response = create_response(client=self.client.post, url='boards:new_topic', data={}, pk=self.board.pk)
        form = invalid_post_response.context.get('form')
        self.assertEquals(invalid_post_response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_empty_fields_post_data(self):
        """
            Invalid post data should not redirect
            The expected behavior is to show the form again with validation errors
        """
        data = {'subject': '',
                'message': ''}
        empty_fields_post_response = create_response(client=self.client.post, url='boards:new_topic', data=data,
                                                     pk=self.board.pk)
        self.assertEquals(empty_fields_post_response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_new_topic_page_contains_form(self):
        response = create_response(client=self.client.get, url='boards:new_topic', pk=1)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

