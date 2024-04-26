from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:title>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("new_page/", views.new_page, name="new_page"),
    path("<str:title>/edit_page/", views.edit_page, name="edit_page"),
    path("random/", views.random, name="random"),
]
