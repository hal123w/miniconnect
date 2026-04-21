from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages # メッセージ用に追加
from .models import Post
from .forms import PostForm, UserUpdateForm, ProfileUpdateForm # プロフィール用フォームを追加

class PostListView(ListView):
    model = Post
    template_name = 'sns/index.html'
    context_object_name = 'posts'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'sns/index.html'
    success_url = reverse_lazy('sns:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

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

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.liked_by.all():
        post.liked_by.remove(request.user)
        liked = False
    else:
        post.liked_by.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'count': post.liked_by.count(),
    })

# --- ここから下が足りなかったプロフィール編集機能です ---
@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'アカウント情報が更新されました！')
            return HttpResponseRedirect(reverse('sns:index'))
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'sns/profile_edit.html', context)