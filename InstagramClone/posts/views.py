from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Post, Comment, Like
from .forms import PostForm, CommentForm
from users.models import Follow

@login_required
def home_feed(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following__id', flat=True)

    posts = Post.objects.filter(user__id__in=following_users).order_by('-created_at')

    return render(request, 'posts/home_feed.html', {'posts': posts})

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



def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')  # top-level only
    comment_form = CommentForm()

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
        'comment_form': comment_form
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

    return render(request, 'posts/delete_comment.html', {'comment': comment})

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        messages.info(request, "You unliked this post.")
    else:
        messages.success(request, "You liked this post.")
    return redirect('post_detail', post_id=post.id)
