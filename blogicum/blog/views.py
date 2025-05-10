
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count

from .models import Post, Category, Comment
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
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/detail.html', {'post': post, 'form': form})



def visible_posts(posts, user):
    """
    Публикации, которые могут появляться НА ПУБЛИЧНЫХ страницах
    (главная, категория, поиск и т. д.).
    """
    return (
        posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
        .order_by('-pub_date')
    )


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
        
    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
        
    return render(request, 'blog/comment.html', {
        'comment': comment,
    })