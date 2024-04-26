import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
import time

from .models import User, Post


def index(request):
    # all posts from all users, with the most recent posts first
    all_posts = Post.objects.all().order_by("-time")

    return render(request, "network/index.html", {"posts": all_posts})


@login_required
def profile(request, user_id):
    profile_owner = User.objects.get(pk=int(user_id))
    posts = profile_owner.posts.all().order_by("-time")
    is_same_user = profile_owner == request.user
    is_follower = profile_owner in request.user.follows.all()
    return render(
        request,
        "network/profile.html",
        {
            "profile_owner": profile_owner,
            "posts": posts,
            "is_same_user": is_same_user,
            "is_follower": is_follower,
        },
    )


@login_required
def following(request):
    followed_authors = request.user.follows.all()
    posts = Post.objects.filter(author__in=followed_authors).all()
    return render(request, "network/following.html", {"posts": posts})

def posts(request, page_num, page_name):
    # get the set of posts for that page name
    if page_name == 'all':
        posts = Post.objects.all().order_by("-time")
    elif page_name == 'following':
        followed_authors = request.user.follows.all()
        posts = Post.objects.filter(author__in=followed_authors).order_by("-time")
    else:
        profile_owner = User.objects.get(pk=int(page_name))
        posts = profile_owner.posts.all().order_by("-time")
    
    post_paginator = Paginator(posts, 10)
    ten_posts_list = post_paginator.page(int(page_num))

    # Make json out of ten_posts_list
    ten_posts_list_json = []
    for post in ten_posts_list:
        post_json = {
            "id": post.id,
            "text": post.text,
            "time": post.time.strftime("%b %d %Y, %I:%M %p"),
            "author_name": post.author.username,
            "author_id": int(post.author.id),
            "edit_btn": request.user.id == post.author.id,
            "liked_by_current_user": request.user in post.liked_by.all(),
            "like_count": post.liked_by.count(),
        }
        ten_posts_list_json.append(post_json)
    btn_info = {
        "next_btn": ten_posts_list.has_next(),
        "previous_btn": ten_posts_list.has_previous(),
    }

    return JsonResponse(
        {"posts": ten_posts_list_json, "btn_info": btn_info}, safe=False
    )


def edit(request, post_id):
    post = Post.objects.get(pk=int(post_id))
    post_text = post.text
    return JsonResponse({"post_text": post_text})

def post(request, post_id):
    post = Post.objects.get(pk=int(post_id))
    return JsonResponse({
        "id": post.id,
        "liked_by_current_user": request.user in post.liked_by.all(),
        "like_count": post.liked_by.count(),

    }, safe=False)


@login_required
def new_post(request):
    if request.method == "POST":
        # Get info from the form and create a post
        p = Post.objects.create(text=request.POST["text"], author=request.user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/new_post.html")


@login_required
def toggle_follow(request, user_id):
    user_to_toggle = User.objects.get(pk=user_id)
    if user_to_toggle not in request.user.follows.all():
        request.user.follows.add(user_to_toggle)
    else:
        request.user.follows.remove(user_to_toggle)
    return HttpResponseRedirect(reverse("profile", args=(user_id,)))


@csrf_exempt
@login_required
def replace_text(request, post_id):

    # Query for requested post
    try:
        post = Post.objects.get(pk=int(post_id))
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Replace text or toggle like
    if request.method == 'PUT':
        data = json.loads(request.body)
        if data.get("text") is not None:
            post.text = data["text"]

            # HERE YOU CAN ALSO TOGGLE LIKE
        if data.get("like") is not None:
            # get the user whose like should be added
            if request.user not in post.liked_by.all():
                post.liked_by.add(request.user)
            else:
                post.liked_by.remove(request.user)          
        post.save()
        return HttpResponse(status=204)
    return JsonResponse({
        "error": "PUT request required"
    }, status=400)
    

def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
