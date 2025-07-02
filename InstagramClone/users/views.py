from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import conf
from django.db.models import Q
from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile,Follow, FollowRequest, Block,SearchHistory
from posts.models import Post
from django.urls import reverse
from django.http import JsonResponse
from notifications.models import Notification
from stories.models import Story,StoryView
from datetime import timedelta
from django.utils import timezone

def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'Username OR password is incorrect')
            

    return render(request, 'users/login.html')

@login_required
def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')

def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            login(request, user)
            return redirect('edit-account')

        else:
            messages.error(
                request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/register.html', context)



@login_required
def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = target_user.profile

    if Block.objects.filter(blocker=target_user, blocked=request.user).exists():
        return redirect(request.GET['next'] if 'next' in request.GET else 'home')

    if Block.objects.filter(blocker=request.user, blocked=target_user).exists():
        return redirect(request.GET['next'] if 'next' in request.GET else 'home')

    is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()
    has_requested = FollowRequest.objects.filter(sender=request.user, receiver=target_user).exists()

    if not profile.is_private or is_following or target_user == request.user:
        posts = target_user.posts.all()
    else:
        posts = []

    recent = timezone.now() - timedelta(hours=24)
    can_view_story = not profile.is_private or is_following or target_user == request.user
    if can_view_story:
        user_stories = Story.objects.filter(user=target_user, created_at__gte=recent).order_by('created_at')
    else:
        user_stories = Story.objects.none()
    has_story = user_stories.exists()
    story_viewed = True
    if has_story and request.user.is_authenticated:
        story_viewed = StoryView.objects.filter(story__in=user_stories, viewer=request.user).count() == user_stories.count()

    context = {
        'target_user': target_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'has_requested': has_requested,
        'post_count': target_user.posts.count(),
        'followers_count': target_user.followers_set.count(),
        'following_count': target_user.following_set.count(),
        'user_stories': user_stories,
        'has_story': has_story,
        'story_viewed': story_viewed,
    }

    return render(request, 'users/profile.html', context)



@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        bio = request.POST.get('bio')
        is_private = request.POST.get('is_private') == 'on'
        profile_image = request.FILES.get('profile_image')

        profile.bio = bio
        profile.is_private = is_private
        if profile_image:
            profile.profile_image = profile_image
        profile.save()
        return redirect('profile', username=request.user.username)

    return render(request, 'users/edit_profile.html', {'profile': profile})


@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()
    blocked_ids = Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
    blocked_by_ids = Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True)

    users = User.objects.none()
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__bio__icontains=query)
        ).exclude(id=request.user.id)\
         .exclude(id__in=blocked_ids)\
         .exclude(id__in=blocked_by_ids)
        if query:
            SearchHistory.objects.get_or_create(user=request.user, keyword=query)

    history = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]

    return render(request, 'users/search.html', {
        'users': users,
        'history': history,
        'query': query
    })




@login_required
def follow_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target == request.user or Block.objects.filter(blocker=target, blocked=request.user).exists():
        return redirect('profile', username=target.username)

    if target.profile.is_private:
        FollowRequest.objects.get_or_create(sender=request.user, receiver=target)
    else:
        Follow.objects.get_or_create(follower=request.user, following=target)
    return redirect('profile', username=target.username)



@login_required
def followers_list_view(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.followers_set.all()
    return render(request, 'users/followers_list.html', {'user': user, 'followers': followers})



@login_required
def following_list_view(request, username):
    user = get_object_or_404(User, username=username)
    following = user.following_set.all()
    return render(request, 'users/following_list.html', {'user': user, 'following': following})



@login_required
def send_follow_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    FollowRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    return redirect('profile', username=receiver.username)



@login_required
def accept_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)
    Follow.objects.get_or_create(follower=follow_request.sender, following=request.user)
    notif = Notification.objects.create(
        sender=request.user,
        receiver=follow_request.sender,
        notification_type='request_accepted',
    )
    print("DEBUG: Notification created:", notif, notif.id)
    follow_request.delete()
    return redirect('profile', username=request.user.username)

@login_required
def reject_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)
    follow_request.delete()
    return redirect('profile', username=request.user.username)



@login_required
def block_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target != request.user:
        Block.objects.get_or_create(blocker=request.user, blocked=target)
        Follow.objects.filter(Q(follower=request.user, following=target) | Q(follower=target, following=request.user)).delete()
        FollowRequest.objects.filter(Q(sender=request.user, receiver=target) | Q(sender=target, receiver=request.user)).delete()
    return redirect(request.GET['next'] if 'next' in request.GET else 'home')


@login_required
def unblock_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Block.objects.filter(blocker=request.user, blocked=target).delete()
    return redirect(request.GET['next'] if 'next' in request.GET else 'home')


@login_required
def blocked_users_list(request):
    blocks = Block.objects.filter(blocker=request.user).select_related('blocked__profile')
    return render(request, 'users/blocked_users.html', {'blocks': blocks})




    

@login_required
def unfollow_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=target).delete()
    return redirect(request.GET['next'] if 'next' in request.GET else 'home')

@login_required
def remove_follower(request, follower_id):
    follower = get_object_or_404(User, id=follower_id)
    Follow.objects.filter(follower=follower, following=request.user).delete()
    return redirect(request.GET['next'] if 'next' in request.GET else 'home')





@login_required
def cancel_follow_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    FollowRequest.objects.filter(sender=request.user, receiver=receiver).delete()
    return redirect('profile', username=receiver.username)


@login_required
def delete_search_history(request, keyword):
    SearchHistory.objects.filter(user=request.user, keyword=keyword).delete()
    return redirect('search-users')



@login_required
def live_search_users(request):
    q = request.GET.get('q', '').strip()
    users = User.objects.all()

    if request.user.is_authenticated:
        users = users.exclude(id=request.user.id)
        blocked_ids = Block.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
        users = users.exclude(id__in=blocked_ids)
        blocked_by_ids = Block.objects.filter(blocked=request.user).values_list('blocker_id', flat=True)
        users = users.exclude(id__in=blocked_by_ids)

    if q:
        users = users.filter(username__icontains=q)

    users = users[:10]
    results = []
    for user in users:
        results.append({
            'username': user.username,
            'profile_image': user.profile.profile_image.url if user.profile.profile_image else '/static/profiles/user-default.png'
        })
    return JsonResponse({'results': results})


@login_required
def deactivate_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user:
            user.delete()
            logout(request)
            messages.success(request, "Your account has been deleted.")
            return redirect('login')
        else:
            messages.error(request, "Incorrect password. Please try again.")
    return render(request, 'users/deactivate_account.html')