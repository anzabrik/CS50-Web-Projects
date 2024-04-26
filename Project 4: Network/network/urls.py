from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_post", views.new_post, name="new_post"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("toggle_follow/<int:user_id>", views.toggle_follow, name="toggle_follow"),
    path("following", views.following, name="following"),

    # API Routes
    path("posts/<int:page_num>/<str:page_name>", views.posts, name="posts"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("replace_text/<int:post_id>", views.replace_text, name="replace_text"),
    path("post/<int:post_id>", views.post, name="post"),
]
