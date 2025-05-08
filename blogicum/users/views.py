
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from blog.models import Post
from .forms import CustomUserCreationForm, ProfileEditForm

User = get_user_model()
POSTS_PER_PAGE = 10


class RegisterView(FormView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'

    def form_valid(self, form):
        usr = form.save()
        login(self.request, usr)
        return redirect('users:profile', username=usr.username)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date')
    page_obj = Paginator(posts, POSTS_PER_PAGE).get_page(
        request.GET.get('page'))
    return render(request, 'users/profile.html',
                  {'author': author, 'page_obj': page_obj})


@login_required
def profile_edit(request, username):
    if request.user.username != username:
        return redirect('users:profile', username=username)
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('users:profile', username=username)
    return render(request, 'users/profile_edit.html', {'form': form})
