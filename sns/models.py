from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    bio = models.TextField(max_length=160, blank=True, verbose_name="自己紹介")

    def __str__(self):
        return f'{self.user.username} Profile'

# ユーザーが作られた時に、自動でプロフィールも作成されるようにする設定
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()