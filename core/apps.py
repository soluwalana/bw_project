from django.apps import AppConfig
from datetime import datetime
import pytz

AUCTIONEER = None

class CoreAppConfig(AppConfig):
    """ Nifty way to get long running processes to run
        at startup """
    name = 'core'
    verbose_name = 'Auctioneer Application'
    
    def ready(self):
        global AUCTIONEER
        try:
            from auctioneer import Auctioneer
            from models import Auction  # Here to avoid 1.9 deprecation warning
            
            AUCTIONEER = Auctioneer()
            # create channels for all the auctions that are still pending
            now = pytz.utc.localize(datetime.now())
            auctions = Auction.objects.filter(expires__gt=now)
            for auction in auctions:
                AUCTIONEER.create(auction, int((auction.expires - now).seconds))
                
        except Exception as err:
            print 'Exception while creating auctioneer,', err
            return
