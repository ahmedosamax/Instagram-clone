from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_story, name='add-story'),
    path('<str:username>/', views.user_stories, name='user-stories'),
    path('delete/<int:story_id>/', views.delete_story, name='delete-story'),
    path('viewers/<int:story_id>/', views.story_viewers, name='story-viewers'),
    path('feed/', views.story_feed, name='story-feed'),

]
