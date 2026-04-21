from django.shortcuts import render, get_object_or_404  # get_object_or_404を追加
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User  # Userモデルのインポートが必要
from django.http import HttpResponseRedirect
from django.urls import reverse

class PostListView(ListView):
    model = Post
    template_name = 'sns/index.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    # ★ここが重要：一覧画面でもフォームを表示できるようにする
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'sns/index.html'
    success_url = reverse_lazy('sns:index')

    def form_valid(self, form):
        # 今ログインしている人を投稿者として自動セット
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('sns:index') # 消した後は一覧に戻る

    def get_queryset(self):
        # 自分の投稿だけを消せるように制限をかける（他人の投稿は消せない）
        return self.model.objects.filter(author=self.request.user)
    
class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # 登録できたらログイン画面へ
    template_name = 'registration/signup.html'

class UserProfileView(ListView):
    model = Post
    template_name = 'sns/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # URLに含まれる「ユーザー名」からその人を探し、その人の投稿だけに絞り込む
        self.user_obj = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=self.user_obj).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 画面に「〇〇さんの投稿一覧」と出すためにユーザー情報を渡す
        context['profile_user'] = self.user_obj
        return context
    
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user) # すでにいいねしてたら消す（解除）
    else:
        post.liked_by.add(request.user)    # まだなら追加する
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('sns:index')))