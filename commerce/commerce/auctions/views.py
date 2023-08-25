from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from datetime import datetime

from .models import User, auction_listing

class listingForm(forms.Form):
    title = forms.CharField(label="listing title", min_length=3, max_length=100, required=True)
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)
    min_bid = forms.IntegerField(label="starting bid", required=True)
    category = forms.CharField(label="Description", max_length=100)
    image_url = forms.URLField(label="image_url", max_length=500, required=True)
    #listing_date = forms.DateTimeField(widget=forms.HiddenInput(), required=False)

# --------------------------Active listings page/default route-----------------------------------
def index(request):
    return render(request, "auctions/index.html", {
        "listings": auction_listing.objects.all()
    })

# ===========================================my work=============================================
# ------------------------------------create listing---------------------------------------------
def create_listing(request):
    if request.method == "POST":
        form = listingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            min_bid = form.cleaned_data['min_bid']
            category = form.cleaned_data['category']
            image_url = form.cleaned_data['image_url']

            new_listing = auction_listing(
                creator=request.user,
                title = title,
                description = description,
                min_bid = min_bid,
                category = category,
                image_url = image_url
            )
            new_listing.save()
            return redirect("index")
    else:
        form = listingForm()
    
    return render(request, "auctions/create_listing.html",{
        "form": form
    })


# ----------------------------------- listing page--------------------------------------------
def listing(request, obj_id):
    listing = auction_listing.objects.get(id=obj_id)
    #bids = bids.objects.get()
    return render(request, "auctions/listing.html", {
        "listing": listing
    })
# =============================================================================================
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
