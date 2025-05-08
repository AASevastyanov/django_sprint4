
from django.urls import path
from . import views
from users import views as users_views

app_name = 'blog'

urlpatterns = [
    # Основные страницы
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),

    # Работа с постами
    path('posts/create/', views.post_create, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='delete_post'),

    # Работа с комментариями
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path(
        'posts/<int:post_id>/comment/<int:comment_id>/edit/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        'posts/<int:post_id>/comment/<int:comment_id>/delete/',
        views.delete_comment,
        name='delete_comment',
    ),

    # Профиль пользователя (под неймспейсом blog)
    path('profile/<str:username>/', users_views.profile, name='profile'),
]
