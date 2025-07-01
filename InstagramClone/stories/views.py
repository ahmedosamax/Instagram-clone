from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Story, StoryView
from django.contrib.auth.models import User

@login_required
def add_story(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '')

        if image:
            Story.objects.create(user=request.user, image=image, caption=caption)
            messages.success(request, "Story added successfully.")
            return redirect('home')
        else:
            messages.error(request, "Please upload an image.")

    return render(request, 'stories/add_story.html')

@login_required
def user_stories(request, username):
    user = get_object_or_404(User, username=username)
    recent = timezone.now() - timedelta(hours=24)
    next_page = request.GET.get('next')

    if next_page == 'profile':
        users_with_stories = [user]
        current_index = 0
    else:
        # Show all users with stories (people you follow), EXCLUDE yourself unless you are viewing your own story
        following_ids = list(request.user.following_set.values_list('following__id', flat=True))
        users_with_stories = (
            User.objects.filter(
                id__in=following_ids,
                stories__created_at__gte=recent
            )
            .distinct()
            .order_by('id')
        )
        users_with_stories = list(users_with_stories)
        # If you are viewing your own story, allow it
        if user == request.user and user not in users_with_stories:
            users_with_stories = [user] + users_with_stories
        current_index = next((i for i, u in enumerate(users_with_stories) if u.username == username), 0)

    stories = Story.objects.filter(user=user, created_at__gte=recent).order_by('created_at')

    if not stories.exists():
        messages.info(request, "No stories available.")
        return redirect('home')

    for story in stories:
        StoryView.objects.get_or_create(story=story, viewer=request.user)

    context = {
        'stories': stories,
        'story_user': user,
        'users_with_stories': users_with_stories,
        'current_user_index': current_index,
    }
    return render(request, 'stories/view_story.html', context)

@login_required
def delete_story(request, story_id):
    story = get_object_or_404(Story, id=story_id, user=request.user)
    story.delete()
    messages.success(request, "Story deleted.")
    return redirect('profile', username=request.user.username)


@login_required
def story_viewers(request, story_id):
    story = get_object_or_404(Story, id=story_id, user=request.user)
    viewers = story.views.select_related('viewer').all()
    return render(request, 'stories/story_viewers.html', {'story': story, 'viewers': viewers})

@login_required
def story_feed(request):
    # Get the list of user IDs the current user follows
    followed_user_ids = request.user.following_set.values_list('following__id', flat=True)

    # Get all non-expired stories from followed users
    stories = Story.objects.filter(
        user__id__in=followed_user_ids,
        is_expired=False
    ).order_by('-created_at')

    return render(request, 'stories/story_feed.html', {'stories': stories})