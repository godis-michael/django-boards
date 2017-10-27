from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve
from ..models import Board, Post, Topic
from ..views import reply_topic
from ..forms import PostReplyForm


class TopicReplyTestCase(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Board', description='Django Board.')
        self.username = 'john'
        self.password = 'test12345'
        user = User.objects.create_user(username=self.username, password=self.password)
        self.topic = Topic.objects.create(subject='Topic', board=self.board, starter=user)
        Post.objects.create(message='test message', topic=self.topic, created_by=user)
        self.url = reverse('boards:reply_topic', kwargs={'board_pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTests(TopicReplyTestCase):
    def test_redirection(self):
        login_url = reverse('accounts:login')
        response = self.client.get(self.url)
        self.assertRedirects(response, f'{login_url}?next={self.url}')


class ReplyTopicTests(TopicReplyTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_reply_topic_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_reply_topic_url_resolves_correct_view(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_navigation_links(self):
        homepage_url = reverse('boards:home')
        board_url = reverse('boards:board_topics', kwargs={'pk': self.board.pk})
        topic_url = reverse('boards:topic_posts', kwargs={'board_pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertContains(self.response, f'href="{homepage_url}"')
        self.assertContains(self.response, f'href="{board_url}"')
        self.assertContains(self.response, f'href="{topic_url}"')

    def test_reply_topic_page_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostReplyForm)

    def test_inputs(self):
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulTopicReplyTests(TopicReplyTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'hello, world!'})

    def test_redirection(self):
        '''
        A valid form submission should redirect the user
        '''
        url = reverse('boards:topic_posts', kwargs={'board_pk': self.board.pk, 'topic_pk': self.topic.pk})
        topic_post_url = f'{url}?page=1#2'
        self.assertRedirects(self.response, topic_post_url)

    def test_reply_created(self):
        '''
        The total post count should be 2
        The one created in the `ReplyTopicTestCase` setUp
        and another created by the post data in this class
        '''
        self.assertEquals(Post.objects.count(), 2)


class InvalidTopicReplyTests(TopicReplyTestCase):
    def setUp(self):
        '''
        Submit an empty dictionary to the `reply_topic` view
        '''
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)