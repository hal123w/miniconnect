from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


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
