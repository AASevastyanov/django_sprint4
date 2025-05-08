
from django.contrib import admin
from django.urls import path, include
from users import views as users_views

urlpatterns = [
    path('profile/<str:username>/', users_views.profile, name='profile'),
    path('auth/registration/', users_views.RegisterView.as_view(),
        name='registration'),

    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('users.urls')),
    path('', include('blog.urls',  namespace='blog')),
    path('', include('pages.urls', namespace='pages')),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
