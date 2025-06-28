from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='inbox'),

    path('chat/<int:user_id>/', views.thread_view, name='thread'),

    path('chat/<int:user_id>/send/', views.send_message, name='send_message'),

    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
]
