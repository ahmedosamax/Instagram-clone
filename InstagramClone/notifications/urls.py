from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list, name='list'),
    path('read/<int:notification_id>/', views.mark_notification_as_read, name='mark_read'),
    path('read_all/', views.mark_all_notifications_as_read, name='mark_all_read'), 
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
]
