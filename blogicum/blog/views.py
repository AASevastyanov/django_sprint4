from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Comment, Category
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'image',
            'category',
            'location',
            'is_published',
            'pub_date',
        ]
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


# Index view: show only published posts up to now
def index(request):
    posts = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


# Post detail view with comment submission
def post_card(request, id):
    try:
        # Authors can view their own drafts or scheduled posts
        post = Post.objects.get(pk=id)
        if not (post.is_published and post.pub_date <= timezone.now()):
            if post.author != request.user:
                raise Post.DoesNotExist
    except Post.DoesNotExist:
        post = get_object_or_404(
            Post,
            pk=id,
            is_published=True,
            pub_date__lte=timezone.now()
        )
    comments = post.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('includes:post_card', id=post.id)
    else:
        form = CommentForm()
    return render(
        request,
        'includes/post_card.html',
        {
            'post': post,
            'comments': comments,
            'comment_form': form
        }
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.annotate(
            comment_count=Count('comments')),
        pk=post_id)
    if (not post.is_published or post.pub_date
            > timezone.now()) and post.author != request.user:
        raise Http404
    comments = post.comments.select_related('author').order_by('created_at')
    form = CommentForm()
    return render(request, 'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})

# Category posts view


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/index.html',
        {
            'page_obj': page_obj,
            'current_category': category
        }
    )


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


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    # adjust request.path so template detects edit mode
    request.path = request.path.replace('/edit/', '/edit_comment/')
    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
    })


@login_required
def delete_comment(request, post_id, comment_id):
    # Если пользователь не автор — будет 404
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)

    if request.method == 'POST':
        # На POST — удаляем и редиректим обратно на detail
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    # adjust request.path so template detects delete mode
    request.path = request.path.replace('/delete/', '/delete_comment/')
    # На GET — просто показываем подтверждение удаления,
    # без формы и без удаления
    return render(request, 'blog/comment.html', {
        'comment': comment,
    })

# User profile view


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        # автор видит все свои посты
        posts = Post.objects.filter(author=profile_user).annotate(
            comment_count=Count('comments')).order_by('-pub_date')
    else:
        # остальные только опубликованные и по опубликованным категориям
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html', {
        'profile_user': profile_user,
        'page_obj': page_obj
    })
