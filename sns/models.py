from django.db import models
from django.contrib.auth.models import User # ユーザー機能を呼び出す

class Post(models.Model):
    # 投稿者（後でログイン機能と繋げるための大事な設定）
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 投稿内容（140文字制限にしてみましょう）
    content = models.CharField(max_length=140)
    # 投稿日時（自動で今の時間が記録される）
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f'{self.author.username}: {self.content[:10]}'