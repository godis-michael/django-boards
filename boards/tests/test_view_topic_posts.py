from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from ..models import Board, Topic, Post
from ..views import PostListView


class TopicPostsTests(TestCase):
    def setUp(self):
        board = Board.objects.create(name='Board', description='Django Board.')
        user = User.objects.create_user(username='john', email='john@mail.com', password='test12345')
        topic = Topic.objects.create(subject='New Topic', board=board, starter=user)
        Post.objects.create(message='Hello World!', topic=topic, created_by=user)
        url = reverse('boards:topic_posts', kwargs={'board_pk': board.pk, 'topic_pk': topic.pk})
        self.response = self.client.get(url)

    def test_topic_posts_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_topic_posts_url_resolves_correct_view(self):
        view = resolve('/boards/1/topics/1/')
        self.assertEquals(view.func.view_class, PostListView)