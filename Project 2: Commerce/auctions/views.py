from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Listing, Bid, Comment, Category
from datetime import date


class NewListingForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "style": "width: 300px;",
                "class": "form-control",
                "label": "Title",
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "label": "Description",
                "style": "width: 300px",
                "class": "form-control",
            }
        )
    )
    starting_price = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "label": "Starting price, $",
                "style": "width: 300px",
                "class": "form-control",
            }
        ),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        label="Category (optional)",
        empty_label="Other",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "style": "width: 300px",
            }
        ),
    )
    image = forms.CharField(
        required=False,
        label="Image url (optional):",
        widget=forms.URLInput(
            attrs={
                "class": "form-control",
                "style": "width: 300px",
            }
        ),
    )


class NewBidForm(forms.Form):
    sum = forms.DecimalField(
        widget=forms.NumberInput(
            attrs={
                "style": "width:300px",
                "class": "form-control",
                "placeholder": "Bid",
            }
        ),
    )
    # user_id", "listing_id", "sum"


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {"listings": listings})


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
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


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
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def new_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_price = form.cleaned_data["starting_price"]
            category = form.cleaned_data["category"]
            if form.cleaned_data["image"]:
                image = form.cleaned_data["image"]
            else:
                image = None
            listing = Listing(
                title=title,
                description=description,
                user=User.objects.get(username=request.user.username),
                starting_price=starting_price,
                image=image,
                category=category,
            )
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        return render(request, "auctions/new_listing.html", {"form": form})
    return render(request, "auctions/new_listing.html", {"form": NewListingForm()})


def listings(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    user = request.user
    message = None
    if not user.is_authenticated:
        return render(
            request,
            "auctions/listing.html",
            {"listing": listing},
        )

    if request.method == "POST":
        form = NewBidForm(request.POST)

        # Check if form data is valid, then work with bid
        if form.is_valid():
            sum = form.cleaned_data["sum"]
            user = request.user
            new_bid = Bid(sum=sum, user=user, listing=listing)
            # If new bid is at least as large as the starting price & there're no old best bids
            if new_bid.sum >= listing.starting_price:
                # If there're previous bids, and if the new bid is greater than any of them
                # a) If there's an old best bid:
                if listing.bids.filter(is_current=True):
                    current_bid = listing.bids.get(is_current=True)
                    # b) And this old best bid is smaller than new
                    if new_bid.sum > current_bid.sum:
                        # The old current loses its current status
                        current_bid.is_current = False
                        # This new bid becomes current bid
                        new_bid.is_current = True
                        new_bid.save()
                        current_bid.save()
                        listing.current_price = new_bid.sum
                        listing.save()
                        message = "Your bid is the current bid"
                    else:
                        message = "ERROR: Your bid is not larger than the current bid"
                else:
                    # If there was no old best bid
                    new_bid.is_current = True  # The new bid becomes current bid
                    new_bid.save()
                    listing.current_price = new_bid.sum
                    listing.save()
                    message = "Your bid is the current bid"

            else:
                # If bid is smaller than the starting price
                # And if there're no old best bids
                if not listing.bids.filter(is_current=True):
                    message = "ERROR: Your bid is not larger than the starting price"
                else:
                    message = "ERROR: Your bid is not larger than the current bid"

    # Add  button "close auction" if user is owner of listing, no matter method POST or GET
    if user == listing.user:
        btn_close_auction = 1
    else:
        btn_close_auction = 0

    # Add  button "in watchlist" or "remove from watchlist", no matter method POST or GET
    # If the listing is in this user's watchlist, display button "remove from watchlist"
    if listing in request.user.watchlist.all():
        btn = 1
    else:
        btn = 0
    comments = Comment.objects.filter(listing=listing)
    # If user is winner, display this info
    if user == listing.winner:
        return render(
            request,
            "auctions/listing.html",
            {"listing": listing, "you_winner": "You have won this auction"},
        )

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "btn": btn,
            "btn_close_auction": btn_close_auction,
            "form": NewBidForm(),
            "message": message,
            "comments": comments,
        },
    )


def watchlist_add_remove(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = Listing.objects.get(pk=listing_id)

    # If the item is not in the user's watchlist
    if listing not in request.user.watchlist.all():
        listing.in_watchlist.add(User.objects.get(pk=request.user.id))
    else:
        listing.in_watchlist.remove(User.objects.get(pk=request.user.id))
    return HttpResponseRedirect(reverse("listings", args=(listing.id,)))


def close_auction(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # Check if there's a highest bid and find highest bidder
    if listing.bids.filter(is_current=True):
        highest_bid = listing.bids.get(is_current=True)
        listing.winner = highest_bid.user
        listing.is_active = False
        listing.save()
        return HttpResponseRedirect(reverse("listings", args=(listing.id,)))


def add_comment(request, listing_id):
    user = request.user
    text = request.POST["text"]
    listing = Listing.objects.get(pk=listing_id)
    comment = Comment(user=user, text=text, listing=listing)
    comment.save()
    return HttpResponseRedirect(reverse("listings", args=(listing.id,)))


def watchlist(request):
    return render(
        request, "auctions/watchlist.html", {"watchlist": request.user.watchlist.all()}
    )


def categories(request):
    return render(
        request, "auctions/categories.html", {"categories": Category.objects.all()}
    )


def category(request, category_name):
    c = Category.objects.get(name=category_name)
    return render(
        request,
        "auctions/category.html",
        {
            "category": c,
            "listings": c.listings_in_this_category.all(),
        },
    )
