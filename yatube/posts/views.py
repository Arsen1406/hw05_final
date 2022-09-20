from django.views.decorators.cache import cache_page
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm
from .ulits import get_paginated_post


@cache_page(20 * 1, key_prefix='index_page')
def index(request):
    post_list = Post.objects.order_by('-pub_date')
    page_obj = get_paginated_post(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = get_paginated_post(request, posts)
    context = {
        'page_obj': page_obj,
        'group': group
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date')
    posts_other = Post.objects.exclude(author=author)
    page_obj = get_paginated_post(request, posts)
    context = {
        'page_obj': page_obj,
        'posts_other': posts_other,
        'author': author,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id).order_by('-created')
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):
    user = request.user
    main = 'Создать пост от имени'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=user.username)

    context = {
        'main': main,
        'user': user,
        'is_edit': False,
        'form': form
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    main = 'Редактировать пост'
    if request.user.id != post.author_id:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'main': main,
        'form': form,
        'is_edit': True,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
