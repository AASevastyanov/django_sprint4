
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=256)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=256)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    pub_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts')
    is_published = models.BooleanField(default=True)
    image = models.ImageField(upload_to='posts_images/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.author} – {self.text[:15]}'
