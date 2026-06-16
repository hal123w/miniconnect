from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'sns'

urlpatterns = [
    # --- 認証系 ---
    path('login/', auth_views.LoginView.as_view(
        template_name='sns/registration/login.html'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='sns/registration/password_change_form.html',
        success_url=reverse_lazy('sns:my_password_change_done')
    ), name='my_password_change'),

    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='sns/registration/password_change_done.html'
    ), name='my_password_change_done'),

    # --- メイン機能 ---
    path('', views.PostListView.as_view(), name='index'),
    path('create/', views.PostCreateView.as_view(), name='create'),
    path('delete/<int:pk>/', views.PostDeleteView.as_view(), name='delete'),
    path('user/<str:username>/', views.UserProfileView.as_view(), name='user_posts'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('like/<int:pk>/', views.like_post, name='like_post'),
    path('user/<str:username>/follow/', views.follow_unfollow, name='follow_unfollow'),
    path('account/delete/', views.account_delete, name='account_delete'),
    path('notifications/', views.notification_list, name='notifications'),
    path('search/', views.search, name='search'),
    path('ranking/', views.ranking, name='ranking'),
]