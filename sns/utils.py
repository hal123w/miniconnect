import re

from .models import Tag

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
