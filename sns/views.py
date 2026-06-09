from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Post, Notification, Profile
from .forms import PostForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import UserCreationForm

# --- 投稿一覧 ---
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'sns/index.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

# --- 新規投稿 ---
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content', 'image']
    template_name = 'sns/post_form.html'
    success_url = reverse_lazy('sns:index')

    def form_valid(self, form):
        form.instance.author = self.request.user  # authorを使用
        return super().form_valid(form)

# --- 投稿削除 ---
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('sns:index')

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

# --- ユーザープロフィール/投稿一覧 ---
class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'sns/user_posts.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        posts = Post.objects.filter(author=profile_user).order_by('-created_at')
        context['posts'] = posts
        context['post_count'] = posts.count()
        return context

# --- サインアップ ---
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'sns/registration/signup.html'
    success_url = reverse_lazy('sns:login')

# --- プロフィール編集 ---
@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('sns:index')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'sns/profile_edit.html', {'form': form})

# --- 【重要】いいね機能（非同期対応版） ---
@csrf_exempt
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    print(f"--- 判定前: {request.user.username} はこの投稿が好き？ {request.user in post.liked_by.all()}")
    
    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        is_liked = False
    else:
        post.liked_by.add(request.user)
        is_liked = True
    
    print(f"--- 判定後: is_likedは {is_liked} になりました。カウントは {post.liked_by.count()}")
    
    return JsonResponse({
        'is_liked': is_liked,
        'like_count': post.liked_by.count(),
    })

# --- フォロー機能 ---
@login_required
def follow_unfollow(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user != target_user:
        if target_user in request.user.profile.following.all():
            request.user.profile.following.remove(target_user)
        else:
            request.user.profile.following.add(target_user)
    return redirect('sns:user_posts', username=username)

# --- 通知一覧 ---
@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'sns/notifications.html', {'notifications': notifications})

# --- アカウント削除 ---
@login_required
def account_delete(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('sns:signup')
    return render(request, 'sns/account_delete_confirm.html')