from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("<int:listing_id>", views.listings, name="listings"),
    path(
        "<int:listing_id>/watchlist_add_remove",
        views.watchlist_add_remove,
        name="watchlist_add_remove",
    ),
    path("<int:listing_id>/close_auction", views.close_auction, name="close_auction"),
    path("<int:listing_id>/add_comment", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("<str:category_name>", views.category, name="category"),
]
