
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count

from .models import Post, Category
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10

def index(request):
    """Главная лента: только опубликованное, уже вышедшее и в опубликованных категориях."""
    posts = (
        Post.objects.annotate(comment_count=Count('comments'))
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
        .order_by('-pub_date')
    )
    page_obj = Paginator(posts, POSTS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = visible_posts(
      category.posts.annotate(comment_count=Count('comments')),
      request.user,
    )
    page_obj = Paginator(
        posts, POSTS_PER_PAGE).get_page(
        request.GET.get('page'))
    return render(
      request,
      'blog/index.html',
      {'category': category, 'page_obj': page_obj},  
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.annotate(
            comment_count=Count('comments')),
        pk=post_id)
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
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
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


def visible_posts(posts, user):
    """Вернуть QuerySet публикаций, видимых для текущего пользователя.

    - Для всех посетителей показываются только опубликованные посты,
      дата публикации которых не позже текущего момента и категория которых опубликована.
    - Автору показываются *все* его посты независимо от даты, категории и статуса публикации.
    Результат отсортирован по дате публикации от новых к старым и без дубликатов.
    """
    base_filter = dict(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )
    public_qs = posts.filter(**base_filter)
    if user.is_authenticated:
        own_qs = posts.filter(author=user)
        qs = (public_qs | own_qs).distinct()
    else:
        qs = public_qs
    return qs.order_by('-pub_date')


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(post.comments, pk=comment_id, author=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/edit_comment.html', {'form': form, 'post': post, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(post.comments, pk=comment_id, author=request.user)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/delete_comment.html', {'post': post, 'comment': comment})

