from django.shortcuts import render


def profile(request, username):
    return render(request, 'users/profile.html', {'username': username})
