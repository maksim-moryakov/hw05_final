from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User

INDEX = reverse('posts:index')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=settings.USER_NAME)
        cls.post = Post.objects.create(
            text=settings.POST_TEXT,
            author=cls.author,
            image=None,
        )

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_page_correct_template(self):
        """Кэширование данных"""
        response = self.client.get(INDEX)
        cached_response_content = response.content
        Post.objects.create(text='Второй пост', author=self.author)
        response = self.client.get(INDEX)
        self.assertEqual(cached_response_content, response.content)
        cache.clear()
        response = self.client.get(INDEX)
        self.assertNotEqual(cached_response_content, response.content)

    def test_index_page_caches_content_for_anonymous(self):
        """Кэшированный контент для неавторизованного пользователя"""
        post = Post.objects.create(
            text='Тестируем кеш',
            author=self.author
        )
        response = self.guest_client.get(INDEX)
        content_old = response.content
        post.delete()
        response = self.guest_client.get(INDEX)
        self.assertEqual(response.content, content_old)
        cache.clear()
        response = self.guest_client.get(INDEX)
        self.assertNotEqual(response.content, content_old)
