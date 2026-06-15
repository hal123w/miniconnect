from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from .models import Post, Notification, Profile
from .forms import PostForm, UserUpdateForm, ProfileUpdateForm
from .utils import sync_post_tags

# --- 投稿一覧 ---
# タブ「フォロー中」: 自分 + フォロー中ユーザーの投稿
# タブ「みんな」: 自分以外かつ未フォローユーザーの投稿
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'sns/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = self.request.user
        tab = self.request.GET.get('tab', 'following')
        followed_user_ids = User.objects.filter(
            profile__in=user.profile.following.all()
        ).values_list('pk', flat=True)

        if tab == 'everyone':
            return Post.objects.exclude(
                author=user
            ).exclude(
                author_id__in=followed_user_ids
            ).order_by('-created_at')

        author_ids = list(followed_user_ids) + [user.pk]
        return Post.objects.filter(author_id__in=author_ids).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = self.request.GET.get('tab', 'following')
        return context

# --- 新規投稿 ---
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'sns/post_form.html'
    success_url = reverse_lazy('sns:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        sync_post_tags(self.object)
        return response

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
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('sns:index')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
    return render(request, 'sns/profile_edit.html', {
        'u_form': u_form,
        'p_form': p_form,
    })

# --- いいね機能（非同期対応版） ---
@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        is_liked = False
    else:
        post.liked_by.add(request.user)
        is_liked = True
        if post.author != request.user:
            Notification.objects.create(
                sender=request.user,
                recipient=post.author,
                notification_type='like',
                post=post,
            )

    return JsonResponse({
        'is_liked': is_liked,
        'like_count': post.liked_by.count(),
    })

# --- フォロー機能 ---
@login_required
def follow_unfollow(request, username):
    target_user = get_object_or_404(User, username=username)
    if request.user != target_user:
        my_profile = request.user.profile
        target_profile = target_user.profile
        if target_profile in my_profile.following.all():
            my_profile.following.remove(target_profile)
        else:
            my_profile.following.add(target_profile)
            Notification.objects.create(
                sender=request.user,
                recipient=target_user,
                notification_type='follow',
            )
    return redirect('sns:user_posts', username=username)

# --- 検索 ---
@login_required
def search(request):
    q = request.GET.get('q', '').strip()
    posts = Post.objects.none()
    users = User.objects.none()

    if q:
        tag_name = q.lstrip('#').lower()
        posts = Post.objects.filter(
            Q(content__icontains=q) | Q(tags__name=tag_name)
        ).distinct().order_by('-created_at')
        users = User.objects.filter(username__icontains=q).order_by('username')

    return render(request, 'sns/search.html', {
        'q': q,
        'posts': posts,
        'users': users,
    })

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
