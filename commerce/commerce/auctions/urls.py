from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listings/<int:obj_id>", views.listing, name="listings"),
    path("add_bid/<int:obj_id>", views.add_bid, name="add_bid"),
    path("pay/<int:obj_id>", views.pay, name="pay"),
    path("item_watchlist/<int:obj_id>", views.item_watchlist, name="item_watchlist"),
    path("rmv_from_watchlist/<int:obj_id>", views.rmv_from_watchlist, name="rmv_from_watchlist"),
    path("close_auction/<int:obj_id>", views.close_auction, name="close_auction"),
    path("my_watchlist", views.my_watchlist, name="my_watchlist"),
    path("comment_section/<int:obj_id>", views.comment_section, name="comment_section"),
    path("categories", views.categories, name="categories"),
    path("category/<str:obj_str>", views.category, name="category")

]
