
from django.contrib import admin
from django.urls import path, include
from users import views as users_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/<str:username>/', users_views.profile, name='profile'),
    path('', include('blog.urls', namespace='blog')),
    path('', include('pages.urls', namespace='pages')),
]
