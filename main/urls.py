from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.video_list, name='video_list'),
    path('reels/', views.reels_list, name='reels_list'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('reel/<int:pk>/', views.reels_list, name='reels_detail'),
    path('video/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('video/<int:pk>/comment_like/<int:id>', views.toggle_comment_like, name='comment_toggle_like'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('search_videos/', views.search_videos, name='search_videos'),
    path('subscribe/<int:user_id>', views.toggle_subscription, name='toggle_subscription'),
    path('user_profile/<int:user_id>', views.user_profile, name='user_profile'),
]