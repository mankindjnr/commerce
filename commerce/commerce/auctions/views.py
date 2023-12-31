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
from rest_framework import exceptions

from .models import User, auction_listing, comments, bids, watchlist, mpesa

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

class mpesaForm(forms.Form):
    phone_num = forms.IntegerField(label="phone_num", required=True)
    pay_amount = forms.IntegerField(label="winning_bid_amount", required=True)

class customError(exceptions.APIException):
    status_code = 400
    default_detailt = "This is a custom error!"

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
    comments_form = commentsForm()
    print("-----------comment section-----------")
    comment_section = False
    if comments.objects.filter(product=listing):
        comment_section = comments.objects.filter(product=listing)
    print(comments.objects.all())
    print("-----------------------------------------")
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
    user_winner = None
    message = None
    paid = None
    max_bidder = None
    mpesa_form = mpesaForm()

    if not is_bid_open:
        winning_bid = max([bid.bid_amount for bid in bid_queryset])
        winner_bid = bids.objects.filter(bid_amount=winning_bid)
        for win in winner_bid:
            winner = win.bidder
    
    # max bidder
    if bids.objects.filter(product=listing):
        largest_bid = max([bid.bid_amount for bid in bid_queryset])
        largest_bidder = bids.objects.filter(bid_amount=largest_bid)

        for large_bidder in largest_bidder:
            if large_bidder.bidder != creator:
                max_bidder = large_bidder.bidder


    # check if the current user is the winner
    if request.user == winner:
        user_winner = True
    
    # check if the product is paid for
    paid_prod = mpesa.objects.filter(product=listing)
    if paid_prod:
        paid = True

    num_of_bids = len(bid_ids)
    max_bid = max([bid.bid_amount for bid in bid_queryset])
    print("-----max-----", max_bid)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "max_bid": max_bid,
        "watching": watching,
        "creator": creator,
        "winner": winner,
        "user_winner": user_winner,
        "max_bidder": max_bidder,
        "mpesa_form": mpesa_form,
        "paid": paid,
        "is_bid_open": is_bid_open,
        "num_of_bids": num_of_bids,
        "the_comments": comment_section,
        "form": form,
        "comment_form": comments_form
    })

# --------------------------------------add_bid------------------------------------------------
def add_bid(request, obj_id):
    if request.method == "POST":
        form = bidForm(request.POST)
        if form.is_valid():
            # instance of the current object
            listing = auction_listing.objects.get(id=obj_id)
            #handling the form data
            amt_of_bid = form.cleaned_data['bid_amount']
            
            print("-------------------listing attr--------")
            bid_queryset = bids.objects.filter(product=listing)
            bid_amts = [bid.bid_amount for bid in bid_queryset]
            print(bid_amts)
            print("---bid_amt---", amt_of_bid)
            print(type(amt_of_bid))
            print("---maxbid---", max(bid_amts))
            print("---typemax---", type(max(bid_amts)))
            if amt_of_bid > max(bid_amts):
                print("its greater")
            else:
                print("not so much")
            print("-------------------------------------------")
            if amt_of_bid <= max(bid_amts):
                print("inside error")
                #raise customError("my error message")
                form.add_error('bid_amount', "Your bid must be greater than the current bid!")
            else:
                print("outside error")
                new_bid = bids(
                    bidder = request.user,
                    product = listing,
                    bid_amount = amt_of_bid
                )
                new_bid.save()
                print("---------new bid------------")
                print(new_bid)
                print("--------------------------")
                return redirect("listings", obj_id=obj_id)
    else:
        form = bidForm()

    return redirect("listings", obj_id=obj_id)
# ----------------------------------pay for product---------------------------------------------
def pay(request, obj_id):
    if request.method == "POST":
        mpesa_form = mpesaForm(request.POST)
        if mpesa_form.is_valid():
            listing = auction_listing.objects.get(id=obj_id)
            phone_num = mpesa_form.cleaned_data['phone_num']
            paid = mpesa_form.cleaned_data['pay_amount']
            print("---------------pay mpesa-------------")
            print(phone_num)
            print(paid)
            print("-------------------------------------------------")

            bid_product = bids.objects.filter(product=listing)
            bid_amts = [bid.bid_amount for bid in bid_product]

            if paid == max(bid_amts):        
                pay_bid = mpesa(
                    payer = request.user,
                    product = listing,
                    paid = paid
                )

                pay_bid.save()
                return redirect("listings", obj_id)
            else:
                error_mess = "amount should match your winning bid"
                return redirect("listings", obj_id)
    else:
        mpesa_form = mpesaForm()

    return redirect("listings", obj_id)

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
# -------------------------------the comment section--------------------------------------------
def comment_section(request, obj_id):
    if request.method == "POST":
        form = commentsForm(request.POST)
        if form.is_valid():
            listing = auction_listing.objects.get(id=obj_id)
            your_comment = form.cleaned_data['the_comment']

            comments_section = comments(
                commenter = request.user,
                product = listing,
                the_comment = your_comment
            )

            comments_section.save()
            return redirect("listings", obj_id)
    else:
        comment_form = commentsForm()
    
    return redirect("listings", obj_id)
#-------------------------------------category-------------------------------------------------
def categories(request):
    return render(request, "auctions/categories.html", {
        "listings": auction_listing.objects.all()
    })     


def category(request, obj_str):
    all_items = auction_listing.objects.filter(category=obj_str)
    return render(request, "auctions/categories.html", {
        "items": all_items
    })
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
