from .models import Notification
from messages_app.models import Thread, Message
from django.db.models import Q


def unread_notifications_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(receiver=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}



def base_context(request):
    has_unread_messages = False
    if request.user.is_authenticated:
        has_unread_messages = Message.objects.filter(
            thread__user1=request.user
        ).filter(~Q(sender=request.user), is_read=False).exists() or \
        Message.objects.filter(
            thread__user2=request.user
        ).filter(~Q(sender=request.user), is_read=False).exists()
    return {'has_unread_messages': has_unread_messages}