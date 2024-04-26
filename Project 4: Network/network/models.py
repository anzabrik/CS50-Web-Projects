from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    follows = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="followed_by"
    )

    def __str__(self):
        return f"{self.username}"


class Post(models.Model):
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, blank=False, on_delete=models.CASCADE, related_name="posts"
    )
    liked_by = models.ManyToManyField(User, blank=True, related_name="liked_posts")

    def __str__(self):
        return f"(Post #{self.id} by {self.author})"