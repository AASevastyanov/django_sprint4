from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from blog.models import Post
from django.core.paginator import Paginator

User = get_user_model()


def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('users:profile', username=user.username)
    return render(request,
                  'registration/registration_form.html',
                  {'form': form})


def profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    all_posts = Post.objects.filter(author=user_obj).order_by('-pub_date')
    paginator = Paginator(all_posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'blog/profile.html', {
        'profile_user': user_obj,
        'page_obj': page_obj,
    })


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('users:profile', username=username)
    form = UserChangeForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('users:profile', username=username)
    return render(request, 'users/edit_profile.html', {'form': form})
