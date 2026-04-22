from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Post(models.Model):
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f'{self.author.username} - {self.content[:10]}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Cloudinaryを使う場合はシンプルにImageFieldだけでOK
    image = models.ImageField(default='default.jpg')
    bio = models.TextField(max_length=160, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

# ユーザー作成時にプロフィールを自動作成するシグナル
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()