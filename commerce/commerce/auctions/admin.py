from django.contrib import admin
from .models import comments, bids, auction_listing, User, watchlist
# Register your models here.

admin.site.register(comments)
admin.site.register(bids)
admin.site.register(auction_listing)
admin.site.register(watchlist)
