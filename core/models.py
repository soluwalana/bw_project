from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Auction(models.Model):
    item_name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024)
    cur_price = models.PositiveIntegerField()
    owner = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

class Bid(models.Model):
    bidder = models.ForeignKey(User)
    auction = models.ForeignKey(Auction)
    bid_amount = models.PositiveIntegerField()
    bid_time = models.DateTimeField(auto_now_add=True)

