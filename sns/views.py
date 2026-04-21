from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin  # 鍵を追加
from django.contrib.auth.decorators import login_required  # 鍵を追加
from django.http import HttpResponseRedirect
from .models import Post
from .forms import PostForm

class PostListView(ListView):
    model = Post
    template_name = 'sns/index.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

# LoginRequiredMixinを追加して「ログイン必須」にする
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'sns/index.html'
    success_url = reverse_lazy('sns:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# LoginRequiredMixinを追加
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('sns:index')

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user)

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class UserProfileView(ListView):
    model = Post
    template_name = 'sns/user_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.user_obj = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=self.user_obj).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.user_obj
        return context

# @login_requiredを追加して「いいね」もログイン必須にする
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
    else:
        post.liked_by.add(request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('sns:index')))