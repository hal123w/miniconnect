from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Notification, Post


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

    def test_like_creates_notification_for_author(self):
        self.client.login(username='liker', password='testpass123')
        self.client.post(reverse('sns:like_post', args=[self.post.pk]))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.author,
                sender=self.liker,
                notification_type='like',
                post=self.post,
            ).exists()
        )

    def test_like_does_not_notify_self(self):
        self.client.login(username='author', password='testpass123')
        own_post = Post.objects.create(author=self.author, content='my post')
        self.client.post(reverse('sns:like_post', args=[own_post.pk]))
        self.assertEqual(Notification.objects.filter(recipient=self.author).count(), 0)


class FollowViewTests(TestCase):
    def setUp(self):
        self.follower = User.objects.create_user(username='follower', password='testpass123')
        self.target = User.objects.create_user(username='target', password='testpass123')

    def test_follow_adds_profile_to_following(self):
        self.client.login(username='follower', password='testpass123')
        self.client.post(reverse('sns:follow_unfollow', args=['target']))
        self.assertIn(
            self.target.profile,
            self.follower.profile.following.all(),
        )

    def test_unfollow_removes_profile_from_following(self):
        self.follower.profile.following.add(self.target.profile)
        self.client.login(username='follower', password='testpass123')
        self.client.post(reverse('sns:follow_unfollow', args=['target']))
        self.assertNotIn(
            self.target.profile,
            self.follower.profile.following.all(),
        )

    def test_follow_creates_notification(self):
        self.client.login(username='follower', password='testpass123')
        self.client.post(reverse('sns:follow_unfollow', args=['target']))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.target,
                sender=self.follower,
                notification_type='follow',
            ).exists()
        )


class ProfileEditViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='editor', password='testpass123')

    def test_profile_edit_returns_200(self):
        self.client.login(username='editor', password='testpass123')
        response = self.client.get(reverse('sns:profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_updates_bio(self):
        self.client.login(username='editor', password='testpass123')
        response = self.client.post(reverse('sns:profile_edit'), {
            'username': 'editor',
            'bio': 'updated bio',
        })
        self.assertEqual(response.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.bio, 'updated bio')


class NotificationListViewTests(TestCase):
    def setUp(self):
        self.recipient = User.objects.create_user(username='recipient', password='testpass123')
        self.sender = User.objects.create_user(username='sender', password='testpass123')

    def test_notifications_page_lists_items(self):
        Notification.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            notification_type='follow',
        )
        self.client.login(username='recipient', password='testpass123')
        response = self.client.get(reverse('sns:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sender')
