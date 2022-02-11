from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Follow, Comment, Group, Post, User


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return redirect('/auth/login/')

    return check_user


def index(request):
    post_list = Post.objects.select_related('group', 'author').all()
    paginator = Paginator(post_list, settings.POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.select_related('group', 'author').all()
    paginator = Paginator(post_list, settings.POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_post_list = Post.objects.select_related(
        'group', 'author').filter(author=user)
    paginator = Paginator(user_post_list, settings.POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(author=user, user=request.user).exists()
    )
    context = {
        'page_obj': page_obj,
        'author': user,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.select_related('author').filter(post=post)
    post_number = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    context = {
        'post_number': post_number,
        'post': post,
        'comments': comments,
        # в процессе.
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list_follow = Post.objects.filter(
        author__in=Follow.objects.filter(user=request.user).values('author'))
    paginator = Paginator(post_list_follow, settings.POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(author=author, user=request.user)
    if request.user != author and not following.exists():
        Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.filter(author=author, user=request.user)
    if request.user != author and unfollow.exists():
        Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username=author)
