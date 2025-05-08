from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from blog.models import Post
from django.utils import timezone

User = get_user_model()


def profile(request, username):
    user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=user).select_related('category')
    if request.user != user:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'users/profile.html', {
        'page_obj': page_obj,
        'profile_user': user,
    })
