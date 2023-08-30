from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listings/<obj_id>", views.listing, name="listings"),
    path("add_bid/<obj_id>", views.add_bid, name="add_bid"),
    path("item_watchlist/<obj_id>", views.item_watchlist, name="item_watchlist"),
    path("rmv_from_watchlist/<obj_id>", views.rmv_from_watchlist, name="rmv_from_watchlist"),
    path("close_auction/<obj_id>", views.close_auction, name="close_auction"),
    path("my_watchlist", views.my_watchlist, name="my_watchlist")
]
