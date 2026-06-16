import calendar
import re
from datetime import datetime

from django.db.models import Count
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


def ranking_posts_queryset():
    """ランキング対象の投稿。visibility フィールドがあれば public のみ。"""
    qs = Post.objects.all()
    if hasattr(Post, 'visibility'):
        qs = qs.filter(visibility='public')
    return qs


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
