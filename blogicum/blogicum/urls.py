from django.contrib import admin
from django.urls import include, path
from blog.views import SignUpView  

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        '',
        include(
            'blog.urls',
            namespace='blog')),
    path(
        'pages/',
        include(
            'pages.urls',
            namespace='pages')),
    path("auth/registration/", views.SignUpView.as_view(), name="registration"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("auth/", include("django.contrib.auth.urls")),
]

handler404 = "blogicum.views.page_not_found"
handler500 = "blogicum.views.server_error"
handler403 = "blogicum.views.csrf_failure"

