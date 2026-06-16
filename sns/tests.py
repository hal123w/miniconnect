from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

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


class HashtagTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tagger', password='testpass123')

    def test_post_create_extracts_hashtags(self):
        self.client.login(username='tagger', password='testpass123')
        self.client.post(reverse('sns:create'), {'content': 'hello #Django world #django'})
        post = Post.objects.get(author=self.user)
        tag_names = set(post.tags.values_list('name', flat=True))
        self.assertEqual(tag_names, {'django'})


class TimelineSplitTests(TestCase):
    def setUp(self):
        self.me = User.objects.create_user(username='me', password='testpass123')
        self.followed = User.objects.create_user(username='followed', password='testpass123')
        self.stranger = User.objects.create_user(username='stranger', password='testpass123')
        self.me.profile.following.add(self.followed.profile)
        Post.objects.create(author=self.me, content='my post')
        Post.objects.create(author=self.followed, content='followed post')
        Post.objects.create(author=self.stranger, content='stranger post')

    def test_following_tab_shows_self_and_followed(self):
        self.client.login(username='me', password='testpass123')
        response = self.client.get(reverse('sns:index') + '?tab=following')
        self.assertContains(response, 'my post')
        self.assertContains(response, 'followed post')
        self.assertNotContains(response, 'stranger post')

    def test_everyone_tab_shows_unfollowed_only(self):
        self.client.login(username='me', password='testpass123')
        response = self.client.get(reverse('sns:index') + '?tab=everyone')
        self.assertContains(response, 'stranger post')
        self.assertNotContains(response, 'my post')
        self.assertNotContains(response, 'followed post')


class SearchViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='findme', password='testpass123')
        self.other = User.objects.create_user(username='other', password='testpass123')
        self.post = Post.objects.create(author=self.other, content='learning #django today')

    def test_search_finds_post_by_tag_without_hash(self):
        from sns.utils import sync_post_tags
        sync_post_tags(self.post)
        self.client.login(username='findme', password='testpass123')
        response = self.client.get(reverse('sns:search'), {'q': 'django'})
        self.assertContains(response, 'learning #django today')

    def test_search_finds_user_by_username(self):
        self.client.login(username='findme', password='testpass123')
        response = self.client.get(reverse('sns:search'), {'q': 'find'})
        self.assertContains(response, 'findme')


class RankingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='rankuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='rankuser2', password='testpass123')
        self.liker = User.objects.create_user(username='liker2', password='testpass123')

    def _make_post_on(self, author, content, year, month, day, hour=12):
        post = Post.objects.create(author=author, content=content)
        tz = timezone.get_current_timezone()
        aware = timezone.make_aware(datetime(year, month, day, hour, 0, 0), tz)
        Post.objects.filter(pk=post.pk).update(created_at=aware)
        post.refresh_from_db()
        return post

    def test_daily_winner_picks_most_likes(self):
        from sns.utils import get_daily_winner

        post1 = self._make_post_on(self.user1, 'post a', 2026, 6, 10)
        post2 = self._make_post_on(self.user2, 'post b', 2026, 6, 10)
        post1.liked_by.add(self.liker)
        post2.liked_by.add(self.liker)
        post2.liked_by.add(self.user1)

        winner = get_daily_winner(2026, 6, 10)
        self.assertEqual(winner.pk, post2.pk)
        self.assertEqual(winner.like_count, 2)

    def test_tie_goes_to_newer_post(self):
        from sns.utils import get_daily_winner

        old = self._make_post_on(self.user1, 'old post', 2026, 6, 15, hour=10)
        new = self._make_post_on(self.user2, 'new post', 2026, 6, 15, hour=14)
        old.liked_by.add(self.liker)
        new.liked_by.add(self.user1)

        winner = get_daily_winner(2026, 6, 15)
        self.assertEqual(winner.pk, new.pk)

    def test_ranking_page_shows_like_count_and_selected_post(self):
        post = self._make_post_on(self.user1, 'winner post', 2026, 6, 20)
        post.liked_by.add(self.liker)
        self.client.login(username='rankuser1', password='testpass123')
        response = self.client.get(reverse('sns:ranking'), {
            'year': 2026, 'month': 6, 'day': 20,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '❤️ 1')
        self.assertContains(response, 'winner post')

    def test_ranking_requires_login(self):
        response = self.client.get(reverse('sns:ranking'))
        self.assertEqual(response.status_code, 302)
