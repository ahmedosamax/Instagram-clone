from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Thread, Message
from django.db.models import Q
from django.contrib import messages
from .forms import MessageEditForm

@login_required
def inbox_view(request):
    threads = Thread.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-created_at')
    return render(request, 'messages_app/inbox.html', {'threads': threads})



@login_required
def thread_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    user1, user2 = sorted([request.user, other_user], key=lambda x: x.id)
    thread, created = Thread.objects.get_or_create(user1=user1, user2=user2)

    thread.messages.filter(sender=other_user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        if 'edit_message_id' in request.POST:
            message_id = request.POST.get('edit_message_id')
            message_obj = get_object_or_404(Message, id=message_id, sender=request.user)
            form = MessageEditForm(request.POST, instance=message_obj)
            if form.is_valid():
                form.save()
                messages.success(request, "Message updated.")
                return redirect('thread', user_id=other_user.id)
        else:
            content = request.POST.get('content')
            if content:
                Message.objects.create(thread=thread, sender=request.user, content=content)
                return redirect('thread', user_id=other_user.id)

    messages_qs = thread.messages.all().order_by('timestamp')
    edit_forms = {msg.id: MessageEditForm(instance=msg) for msg in messages_qs if msg.sender == request.user}

    context = {
        'thread': thread,
        'messages': messages_qs,
        'edit_forms': edit_forms,
        'other_user': other_user,
    }
    return render(request, 'messages_app/thread.html', context)


@login_required
def send_message(request, user_id):
    if request.method == 'POST':
        other_user = get_object_or_404(User, id=user_id)

        user1, user2 = sorted([request.user, other_user], key=lambda x: x.id)
        thread, created = Thread.objects.get_or_create(user1=user1, user2=user2)

        content = request.POST.get('content')
        if content:
            Message.objects.create(
                thread=thread,
                sender=request.user,
                content=content
            )
        return redirect('thread', user_id=other_user.id)
    return redirect('inbox')


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender != request.user:
        return HttpResponseForbidden("You can only delete your own messages.")

    thread = message.thread
    message.delete()
    messages.success(request, "Message deleted.")
    return redirect('thread', user_id=thread.user1.id if thread.user1 != request.user else thread.user2.id)