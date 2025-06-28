from django.urls import path
from . import views


urlpatterns = [
    path('', views.notifications_list, name='list'),  # /notifications/
    path('read/<int:notification_id>/', views.mark_notification_as_read, name='mark_read'),  # /notifications/read/5/
    path('read_all/', views.mark_all_notifications_as_read, name='mark_all_read'),  # /notifications/read_all/
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),  # /notifications/delete/5/
]
