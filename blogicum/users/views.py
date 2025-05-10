from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from blog.models import Post
from django.utils import timezone

User = get_user_model()


def profile(request, username):
    user = get_object_or_404(User, username=username)
    
    posts = Post.objects.filter(author=user).select_related('category', 'author')
    if request.user != user:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'users/profile.html', {
        'profile_user': user,
        'page_obj': page_obj,
        'profile': user 
    })

from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class RegisterView(CreateView):
    """Регистрация нового пользователя."""
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля текущего пользователя."""
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'users/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.request.user.username})


# Для совместимости со существующими ссылками
profile_edit = ProfileEditView.as_view()

