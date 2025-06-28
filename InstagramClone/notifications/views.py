from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'notifications/notifications_list.html', {'notifications': notifications})


@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications:list')


@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    notification.delete()
    return redirect('notifications:list')
