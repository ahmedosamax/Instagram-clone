from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import conf
from django.db.models import Q
from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile,Follow, FollowRequest, Block
from posts.models import Post

def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

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
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')

        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'users/login_register.html')

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

            messages.success(request, 'User account was created!')

            login(request, user)
            return redirect('edit-account')

        else:
            messages.success(
                request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)

# --------------------------------------------
# PROFILE VIEWS
# --------------------------------------------

@login_required
def profile_view(request, username):
    target_user = get_object_or_404(User, username=username)

    # Block check
    if Block.objects.filter(blocker=target_user, blocked=request.user).exists():
        messages.error(request, "You are blocked by this user.")
        return redirect('home')

    if Block.objects.filter(blocker=request.user, blocked=target_user).exists():
        messages.error(request, "You have blocked this user.")
        return redirect('home')

    profile = target_user.profile
    posts = target_user.posts.all()
    is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()
    has_requested = FollowRequest.objects.filter(sender=request.user, receiver=target_user).exists()

    context = {
        'target_user': target_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'has_requested': has_requested
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
        messages.success(request, "Profile updated.")
        return redirect('profile', username=request.user.username)

    return render(request, 'users/edit_profile.html', {'profile': profile})


@login_required
def search_users(request):
    query = request.GET.get("q")
    users = []
    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    return render(request, "users/search.html", {"users": users})

# --------------------------------------------
# FOLLOW SYSTEM
# --------------------------------------------

@login_required
def follow_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target == request.user or Block.objects.filter(blocker=target, blocked=request.user).exists():
        return redirect('profile', username=target.username)

    if target.profile.is_private:
        FollowRequest.objects.get_or_create(sender=request.user, receiver=target)
        messages.info(request, "Follow request sent.")
    else:
        Follow.objects.get_or_create(follower=request.user, following=target)
        messages.success(request, f"You are now following {target.username}.")
    return redirect('profile', username=target.username)


@login_required
def unfollow_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=target).delete()
    messages.success(request, f"You unfollowed {target.username}.")
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

# --------------------------------------------
# FOLLOW REQUESTS
# --------------------------------------------

@login_required
def send_follow_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    FollowRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    messages.info(request, "Follow request sent.")
    return redirect('profile', username=receiver.username)


@login_required
def accept_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)
    Follow.objects.get_or_create(follower=follow_request.sender, following=request.user)
    follow_request.delete()
    messages.success(request, f"You accepted {follow_request.sender.username}'s follow request.")
    return redirect('profile', username=request.user.username)


@login_required
def reject_follow_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, receiver=request.user)
    follow_request.delete()
    messages.info(request, "Follow request rejected.")
    return redirect('profile', username=request.user.username)

# --------------------------------------------
# BLOCK SYSTEM
# --------------------------------------------

@login_required
def block_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target != request.user:
        Block.objects.get_or_create(blocker=request.user, blocked=target)
        Follow.objects.filter(Q(follower=request.user, following=target) | Q(follower=target, following=request.user)).delete()
        FollowRequest.objects.filter(Q(sender=request.user, receiver=target) | Q(sender=target, receiver=request.user)).delete()
        messages.warning(request, f"You blocked {target.username}.")
    return redirect('profile', username=target.username)


@login_required
def unblock_user(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Block.objects.filter(blocker=request.user, blocked=target).delete()
    messages.success(request, f"You unblocked {target.username}.")
    return redirect('profile', username=target.username)


@login_required
def blocked_users_list(request):
    blocks = Block.objects.filter(blocker=request.user)
    return render(request, 'users/blocked_users.html', {'blocks': blocks})







    

