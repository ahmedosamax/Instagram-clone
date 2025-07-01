from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from .models import Post, Comment, Like
from .forms import PostForm, CommentForm
from users.models import Follow
from stories.models import Story, StoryView
from datetime import timedelta
from django.utils import timezone
@login_required
def home_feed(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following__id', flat=True)
    posts = Post.objects.filter(user__id__in=following_users).order_by('-created_at')

    liked_post_ids = Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True)

    # --- STORIES FEATURE START ---
    recent = timezone.now() - timedelta(hours=24)
    story_users = list(following_users) + [request.user.id]
    all_stories = (
        Story.objects.filter(user__id__in=story_users, created_at__gte=recent)
        .select_related('user')
        .order_by('user', '-created_at')
    )
    # Get latest story per user in Python (works on all DBs)
    latest_stories_dict = {}
    for story in all_stories:
        if story.user_id not in latest_stories_dict:
            latest_stories_dict[story.user_id] = story
    latest_stories = list(latest_stories_dict.values())

    # Build stories_info for the stories bar
    stories_info = []
    for story in latest_stories:
        user = story.user
        user_stories = [s for s in all_stories if s.user_id == user.id]
        has_story = bool(user_stories)
        story_viewed = True
        if has_story and request.user.is_authenticated:
            viewed_count = StoryView.objects.filter(story__in=user_stories, viewer=request.user).count()
            story_viewed = viewed_count == len(user_stories)
        stories_info.append({
            'user': user,
            'profile_image': user.profile.profile_image.url if hasattr(user.profile, 'profile_image') and user.profile.profile_image else None,
            'has_story': has_story,
            'story_viewed': story_viewed,
        })

    your_story = any(story.user_id == request.user.id for story in latest_stories)
    # --- STORIES FEATURE END ---

    return render(request, 'posts/home_feed.html', {
        'posts': posts,
        'liked_post_ids': liked_post_ids,
        'stories_info': stories_info,  # for the stories bar with ring logic
        'your_story': your_story,      # for the "Your Story" logic
    })

@login_required
def create_post(request):
    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Error creating post.')

    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    form = PostForm(instance=post)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated.')
            return redirect('post_detail', post_id=post.id)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('home')

    return render(request, 'posts/delete_post.html', {'post': post})



@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')  # top-level only
    comment_form = CommentForm()

    # ✅ Get liked user IDs
    liked_user_ids = post.likes.values_list('user_id', flat=True)

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post

            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
                if parent_comment:
                    new_comment.parent = parent_comment

            new_comment.save()
            messages.success(request, 'Comment added.')
            return redirect('post_detail', post_id=post.id)

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'liked_user_ids': liked_user_ids,  # ✅ pass to template
    })


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    form = CommentForm(instance=comment)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated.")
            return redirect('post_detail', post_id=comment.post.id)

    return render(request, 'posts/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post

    if request.user != comment.user and request.user != post.user:
        messages.error(request, "You don't have permission to delete this comment.")
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect('post_detail', post_id=post.id)

    return render(request, 'posts/delete_comment.html', {'comment': comment, 'post': post})



@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        # Optionally: messages.info(request, "You unliked this post.")
    else:
        # Optionally: messages.success(request, "You liked this post.")
        pass
    return HttpResponse(status=204)  # No Content, no redirect
