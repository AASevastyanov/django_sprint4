
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count, Q

from .models import Post, Category
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10


def _visible(posts, user):
    base = posts.filter(is_published=True, pub_date__lte=timezone.now())
    if user.is_authenticated:
        base = posts.filter(Q(author=user) | Q(
            is_published=True, pub_date__lte=timezone.now()))
    return base


def index(request):
    posts = _visible(Post.objects.annotate(
        comment_count=Count('comments')), request.user)
    page_obj = Paginator(posts, POSTS_PER_PAGE).get_page(
        request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = _visible(category.posts.annotate(
        comment_count=Count('comments')), request.user)
    page_obj = Paginator(posts, POSTS_PER_PAGE).get_page(
        request.GET.get('page'))
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.annotate(
        comment_count=Count('comments')), pk=post_id)
    if (not post.is_published or post.pub_date
            > timezone.now()) and post.author != request.user:
        return redirect('blog:index')
    comments = post.comments.select_related('author')
    form = CommentForm()
    return render(request, 'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        return redirect('users:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('users:profile', username=request.user.username)
    return render(request, 'blog/delete_post.html', {'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        cm = form.save(commit=False)
        cm.post = post
        cm.author = request.user
        cm.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/detail.html', {'post': post, 'form': form})
