from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User


class User(AbstractUser):
    # username, email, password,
    pass


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings_made"
    )
    starting_price = models.DecimalField(decimal_places=2, max_digits=6)
    current_price = models.DecimalField(decimal_places=2, max_digits=6, default=0)
    in_watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    is_active = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="listings_in_this_category",
    )
    winner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="won_auctions",
    )
    image = models.URLField(max_length=400, blank=True, null=True)
    DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

    def __str__(self):
        return f"{self.title}: starting_price: {self.starting_price}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_to")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    sum = models.DecimalField(decimal_places=2, max_digits=6)
    time = models.DateTimeField(auto_now_add=True)
    is_current = models.BooleanField(default=False)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_to")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments_from"
    )
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
