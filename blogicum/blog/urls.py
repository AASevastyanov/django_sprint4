
from django.urls import path
from . import views
app_name = 'blog'
urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:slug>/', views.category_posts, name='category'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'),
]
