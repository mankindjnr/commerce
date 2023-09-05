from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class auction_listing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    min_bid = models.IntegerField()
    category = models.CharField(max_length=100)
    image_url = models.URLField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)
    bid_open = models.BooleanField(default=True)
    # add time later(correct current time)

    def __str__(self):
        return f"{self.title} id:{self.id} time: {self.timestamp.strftime('%B %d, %Y %H:%M:%S')}"

class watchlist(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(auction_listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"user:{self.watcher} prod:{self.product}"

class bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(auction_listing, on_delete=models.CASCADE)
    bid_amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} me:{self.bidder}: {self.product} {self.bid_amount}"

class comments(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(auction_listing, on_delete=models.CASCADE)
    the_comment = models.TextField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)
