
from django.contrib import admin
from django.urls import path, include
from users import views as users_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/<str:username>/', users_views.profile, name='profile'),
    path('', include('blog.urls', namespace='blog')),
    path('', include('pages.urls', namespace='pages')),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
