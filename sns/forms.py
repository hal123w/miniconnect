from django import forms
from django.contrib.auth.models import User
from .models import Post, Profile

# 投稿用のフォーム
class PostForm(forms.ModelForm):
    mutual_only = forms.BooleanField(
        required=False,
        label='相互フォローのみ閲覧可',
    )

    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '今何してる？（140文字以内） #django のようにタグ付け可',
                'rows': 3,
            }),
        }

    def save(self, commit=True):
        post = super().save(commit=False)
        if self.cleaned_data.get('mutual_only'):
            post.visibility = Post.Visibility.MUTUAL_ONLY
        else:
            post.visibility = Post.Visibility.PUBLIC
        if commit:
            post.save()
            self.save_m2m()
        return post

# --- ここから下がプロフィール編集に必要です ---

# ユーザー名変更用
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

# プロフィール画像・自己紹介用
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }