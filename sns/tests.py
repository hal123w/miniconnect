from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Post


class IndexViewTests(TestCase):
    def test_index_requires_login(self):
        response = self.client.get(reverse('sns:index'))
        login_url = reverse('sns:login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(login_url))

    def test_index_returns_200_when_logged_in(self):
        User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sns:index'))
        self.assertEqual(response.status_code, 200)


class PostDeleteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='testpass123')
        self.other = User.objects.create_user(username='other', password='testpass123')
        self.post = Post.objects.create(author=self.author, content='delete me')

    def test_author_can_delete_own_post(self):
        self.client.login(username='author', password='testpass123')
        response = self.client.post(reverse('sns:delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_non_author_gets_404_on_delete(self):
        self.client.login(username='other', password='testpass123')
        response = self.client.post(reverse('sns:delete', args=[self.post.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())


class LikePostViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author', password='testpass123')
        self.liker = User.objects.create_user(username='liker', password='testpass123')
        self.post = Post.objects.create(author=self.author, content='like me')

    def test_post_toggles_like(self):
        self.client.login(username='liker', password='testpass123')
        url = reverse('sns:like_post', args=[self.post.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_liked'])
        self.assertEqual(data['like_count'], 1)

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['is_liked'])
        self.assertEqual(data['like_count'], 0)

    def test_get_is_not_allowed(self):
        self.client.login(username='liker', password='testpass123')
        response = self.client.get(reverse('sns:like_post', args=[self.post.pk]))
        self.assertEqual(response.status_code, 405)
