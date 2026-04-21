from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    content = forms.CharField(
        label='',
        max_length=140, # 最大140文字に制限
        min_length=1,   # 空文字を禁止
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '今何してる？（140文字以内）',
            'rows': 3,
        })
    )

    class Meta:
        model = Post
        fields = ['content']