import re
from datetime import datetime

from django.db.models import Count, Q
from django.utils import timezone

from .models import Post, Tag

# # の直後: 英数字・日本語（ひらがな・カタカナ・漢字）
HASHTAG_PATTERN = re.compile(r'#([\wぁ-んァ-ヶ一-龥]+)')


def extract_hashtag_names(text):
    """本文からハッシュタグ名を抽出し、小文字・重複なしで返す。"""
    names = HASHTAG_PATTERN.findall(text)
    return list(dict.fromkeys(name.lower() for name in names))


def sync_post_tags(post):
    """投稿本文からタグを抽出し、Post.tags を更新する。"""
    tag_objects = []
    for name in extract_hashtag_names(post.content):
        tag, _ = Tag.objects.get_or_create(name=name)
        tag_objects.append(tag)
    post.tags.set(tag_objects)


def is_mutual_follow(user_a, user_b):
    """A→B かつ B→A の相互フォローか。"""
    if user_a.pk == user_b.pk:
        return False
    return (
        user_b.profile in user_a.profile.following.all()
        and user_a.profile in user_b.profile.following.all()
    )


def get_mutual_follow_user_ids(user):
    """指定ユーザーと相互フォローのユーザー ID 一覧。"""
    mutual_ids = []
    for profile in user.profile.following.all():
        if is_mutual_follow(user, profile.user):
            mutual_ids.append(profile.user_id)
    return mutual_ids


def can_view_post(viewer, post):
    """閲覧者が投稿を見られるか。"""
    if post.author_id == viewer.pk:
        return True
    if post.visibility == Post.Visibility.PUBLIC:
        return True
    if post.visibility == Post.Visibility.MUTUAL_ONLY:
        return is_mutual_follow(viewer, post.author)
    return False


def posts_visible_to(user, queryset):
    """閲覧者に見える投稿だけに絞る（検索・プロフィール用）。"""
    mutual_ids = get_mutual_follow_user_ids(user)
    return queryset.filter(
        Q(visibility=Post.Visibility.PUBLIC)
        | Q(visibility=Post.Visibility.MUTUAL_ONLY, author_id__in=mutual_ids)
        | Q(author=user)
    ).distinct()


def ranking_posts_queryset():
    """ランキング対象: 通常公開のみ。"""
    return Post.objects.filter(visibility=Post.Visibility.PUBLIC)


def _month_bounds(year, month):
    tz = timezone.get_current_timezone()
    start = timezone.make_aware(datetime(year, month, 1), tz)
    if month == 12:
        end = timezone.make_aware(datetime(year + 1, 1, 1), tz)
    else:
        end = timezone.make_aware(datetime(year, month + 1, 1), tz)
    return start, end


def get_monthly_daily_winners(year, month):
    """
    各日の代表投稿（その日に作成された投稿のうちいいね最多、同点は新しい方）。
    戻り値: {day: post}（post には like_count が annotate 済み）
    """
    start, end = _month_bounds(year, month)
    posts = ranking_posts_queryset().filter(
        created_at__gte=start,
        created_at__lt=end,
    ).annotate(like_count=Count('liked_by'))

    winners = {}
    for post in posts:
        day = timezone.localtime(post.created_at).day
        if day not in winners:
            winners[day] = post
            continue
        current = winners[day]
        if (post.like_count, post.created_at) > (current.like_count, current.created_at):
            winners[day] = post
    return winners


def get_daily_winner(year, month, day):
    return get_monthly_daily_winners(year, month).get(day)
