from threading import Lock, Timer
from datetime import datetime
from collections import defaultdict
from models import Bid
from django.db.models import F
import time, pusher, re, os
    

class Auctioneer(object):
    """ Singleton class that will manage timeouts of auctions and
        the notification of bids on auctions """
    
    def __init__(self):
        # Not Sure if pusher.Pusher object is thread safe, so assume it isn't
        self.push_lock = Lock()

        self.push, self.key, self.secret, self.app_id = (None, None, None, None)
                
        url = os.environ.get(
            'PUSHER_URL',
            'http://6c26621f31ef7307ee0b:90c16ef8025db847d5d0@api.pusherapp.com/apps/137638'
        )
        
        match = re.search('https?://(\w+):(\w+)@[\w\./]*?(\d+)$', url)
        
        if not match:
            print "Can Not Initialize pusher!!"
            return

        self.key, self.secret, self.app_id = match.groups()

        print self.key, self.secret, self.app_id
        
        self.push = pusher.Pusher(
            app_id=self.app_id,
            key=self.key,
            secret=self.secret,
            ssl=True,
            port=443
        )

    def create(self, auction, duration):
        """ Creates a new auction channel """
        if not self.push:
            return
        
        timer = Timer(duration, lambda:
              self.end(auction)
        )
        timer.daemon = True
        timer.start()
        with self.push_lock:
            self.push.trigger('private-auction-' + str(auction.id), 'created', {
                'created': 'Awwwwww Yeah!! Lets get this show on the road'
            })
        
    def authenticate(self, channel, socket):
        """ Proxy authenticate with the lock held """
        if not self.push:
            return
            
        with self.push_lock:
            return self.push.authenticate(
                channel=channel, socket_id=socket
            )
    
    def end(self, auction):
        """ End the current acution """
        if not self.push:
            return
            
        auction.refresh_from_db()
        bids = Bid.objects.filter(auction=auction, bid_amount=F('auction__cur_price'))
        winner_id = None
        if len(bids) > 0:
            winner_id = bids[0].bidder.id
        
        with self.push_lock:
            self.push.trigger('private-auction-' + str(auction.id), 'update', {
                'ended': 'This Auction is Now Over',
                'purchase_price': auction.cur_price,
                'winner_id': winner_id
            })
            
    def bid(self, auction, bid):
        """ Update the bid of this auction """
        if not self.push:
            return
            
        with self.push_lock:
            print auction.id, 'biding', bid.bid_amount
            self.push.trigger('private-auction-' + str(auction.id), 'update', {
                'bid_activity': 'This auction has had its bid increased',
                'bid': {
                    'amount': bid.bid_amount,
                    'time': bid.bid_time.strftime('%a, %d %b %Y %H:%M:%S'),
                    'bidder_id': bid.bidder.id
                }                    
            })
