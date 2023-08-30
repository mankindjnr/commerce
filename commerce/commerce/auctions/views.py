from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django import forms
from datetime import datetime
from pprint import pprint

from .models import User, auction_listing, comments, bids, watchlist

class listingForm(forms.Form):
    title = forms.CharField(label="listing title", min_length=3, max_length=100, required=True)
    description = forms.CharField(label="Description", widget=forms.Textarea, required=True)
    min_bid = forms.IntegerField(label="starting bid", required=True)
    category = forms.CharField(label="Description", max_length=100)
    image_url = forms.URLField(label="image_url", max_length=500, required=True)

class bidForm(forms.Form):
    bid_amount = forms.IntegerField(label="bid amount", required=True)

class commentsForm(forms.Form):
    the_comment = forms.CharField(label="comment section", widget=forms.Textarea, required=True)
# --------------------------Active listings page/default route-----------------------------------
def index(request):
    #all_bids = bids.objects.all()
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
            print("-----------new_listing------------")
            print(new_listing)
            print("-----------------------------------")
            original_bid = bids(
                bidder = request.user,
                product = new_listing,
                bid_amount = min_bid
            )
            original_bid.save()

            print("------------original bid--------------")
            print(original_bid)
            print("----------------------------------")
            return redirect("index")
    else:
        form = listingForm()
    
    return render(request, "auctions/create_listing.html",{
        "form": form
    })
#--------------------------------------close auction-----------------------------------------
def close_auction(request, obj_id):
    if request.method == "POST":
        try:
            listing = auction_listing.objects.get(id=obj_id)
            listing.bid_open = False
            listing.save()
        except auction_listing.DoesNotExist:
            return redirect("index")
    
    return redirect("listings", obj_id)

# ----------------------------------- listing page--------------------------------------------
def listing(request, obj_id):
    listing = auction_listing.objects.get(id=obj_id)
    print("----------------listing--------------")
    print(listing)
    print(listing.id)
    print("--------------bid print with id----------------------")
    bid_queryset = bids.objects.filter(product=listing)
    bid_ids = [bid.id for bid in bid_queryset]
    print(bid_ids)
    print("-------------------------------------")
    form = bidForm()

    # watchlist
    watching = False
    if watchlist.objects.all() is not None:
        if watchlist.objects.filter(watcher=request.user, product=listing):
            watching = True
    
    #creator
    creator = False
    if request.user == listing.creator:
        creator = True
    
    #is bid open
    is_bid_open = listing.bid_open

    #auction winner
    winner = None

    if not is_bid_open:
        winning_bid = max([bid.bid_amount for bid in bid_queryset])
        winner_bid = bids.objects.filter(bid_amount=winning_bid)
        for win in winner_bid:
            winner = win.bidder

    num_of_bids = len(bid_ids)
    max_bid = max([bid.bid_amount for bid in bid_queryset])
    print("-----max-----", max_bid)

    messages.success(request, "ADDED TO WATCHLIST!")

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "max_bid": max_bid,
        "watching": watching,
        "creator": creator,
        "winner": winner,
        "is_bid_open": is_bid_open,
        "num_of_bids": num_of_bids,
        #"comments": comments,
        "form": form
    })

# --------------------------------------add_bid------------------------------------------------
def add_bid(request, obj_id):
    if request.method == "POST":
        form = bidForm(request.POST)
        if form.is_valid():
            # instance of the current object
            listing = auction_listing.objects.get(id=obj_id)
            #handling the form data
            bid_amount = form.cleaned_data['bid_amount']
            
            print("-------------------listing attr--------")
            bid_queryset = bids.objects.filter(product=listing)
            bid_amts = [bid.bid_amount for bid in bid_queryset]
            print(bid_amts)
            print("---bid_amt---", bid_amount)
            print(type(bid_amount))
            print("---maxbid---", max(bid_amts))
            print("---typemax---", type(max(bid_amts)))
            if bid_amount > max(bid_amts):
                print("its greater")
            else:
                print("not so much")
            print("-------------------------------------------")
            if bid_amount <= max(bid_amts):
                print("inside error")
                form.add_error('bid_amount', "Your bid must be greater than the current bid!")
            else:
                print("outside error")
                new_bid = bids(
                    bidder = request.user,
                    product = listing,
                    bid_amount = bid_amount
                )
                new_bid.save()
                print("---------new bid------------")
                print(new_bid)
                print("--------------------------")
                return redirect("listings", obj_id=obj_id)
    else:
        form = bidForm()

    return redirect("listings", obj_id=obj_id)

#-----------------------------------watchlist---------------------------------------------------
def item_watchlist(request, obj_id):
    if request.method == "POST":
        print("adding to watchlist")
        the_prod = auction_listing.objects.get(id=obj_id)
        
        print("--current--", request.user)
        watching = watchlist(
            watcher = request.user,
            product = the_prod
        )

        watching.save()
        print("--------------watchlist status------------")
        print(watchlist.objects.filter(watcher=request.user))
        print("----------------------------------------")
        return redirect("listings", obj_id=obj_id)
#----------------------------------------view watchlist-----------------------------------------
def my_watchlist(request):
    watchlist_prod = watchlist.objects.filter(watcher=request.user)
    print("============product=================")
    for prod in watchlist_prod:
        print(prod.product.title)
    print("====================================")
    return render(request, "auctions/watchlist.html", {
        "products": watchlist_prod
    })
#------------------------------------remove from watchlist--------------------------------------
def rmv_from_watchlist(request, obj_id):
    if request.method == "POST":
        print("removing from watchlist")
        try:
            item = auction_listing.objects.get(id=obj_id)
            item_to_del = watchlist.objects.filter(watcher=request.user, product=item)
            item_to_del.delete()
            return redirect("listings", obj_id)
        except watchlist.DoesNotExist:
            return redirect("index")
    
    return redirect("listings", obj_id)
# ==============================================================================================
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
