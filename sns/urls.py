from django.urls import path
from .views import PostListView, PostCreateView, PostDeleteView, SignUpView, UserProfileView, like_post

app_name = 'sns'

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('create/', PostCreateView.as_view(), name='create'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='delete'),
    path('user/<str:username>/', UserProfileView.as_view(), name='user_posts'),
    path('post/<int:pk>/like/', like_post, name='like_post'),
]