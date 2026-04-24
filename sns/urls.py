from django.urls import path
from . import views

app_name = 'sns'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('create/', views.PostCreateView.as_view(), name='create'),
    path('delete/<int:pk>/', views.PostDeleteView.as_view(), name='delete'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user_posts'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    # いいね用URL
    path('like/<int:pk>/', views.like_post, name='like_post'),
]