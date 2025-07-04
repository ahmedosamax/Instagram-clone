from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth
    path('', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),

    # Profile
    path('edit/', views.edit_profile, name='edit-account'),
    path('search/', views.search_users, name='search-users'),
    path('live-search/', views.live_search_users, name='live-search-users'),
    path('search/delete/<str:keyword>/', views.delete_search_history, name='delete-search-history'),
    path('profile/<str:username>/', views.profile_view, name='profile'),

    # Follow system
    path('follow/<int:user_id>/', views.follow_user, name='follow-user'),
    path('remove-follower/<int:follower_id>/', views.remove_follower, name='remove-follower'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),
    path('followers/<str:username>/', views.followers_list_view, name='followers-list'),
    path('following/<str:username>/', views.following_list_view, name='following-list'),

    # Follow requests (for private profiles)
    path('cancel-follow-request/<int:user_id>/', views.cancel_follow_request, name='cancel-follow-request'),

    path('follow-request/send/<int:user_id>/', views.send_follow_request, name='send-follow-request'),
    path('follow-request/accept/<int:request_id>/', views.accept_follow_request, name='accept-follow-request'),
    path('follow-request/reject/<int:request_id>/', views.reject_follow_request, name='reject-follow-request'),

    # Blocking system
    path('block/<int:user_id>/', views.block_user, name='block-user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock-user'),
    path('blocked-users/', views.blocked_users_list, name='blocked-users'),
    path('deactivate/', views.deactivate_account, name='deactivate-account'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]