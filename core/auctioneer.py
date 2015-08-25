from threading import Lock, Timer
from datetime import datetime
from collections import defaultdict
from models import Bid
from django.db.models import F
import time, pusher
    

class Auctioneer(object):
    """ Singleton class that will manage timeouts of auctions and
        the notification of bids on auctions """
    
    def __init__(self):
        self.push_lock = Lock()

        # Not Sure if this is thread safe, so assume it isn't
        self.push = pusher.Pusher(
            app_id='137304',
            key='6f1c0b6c435fb05bea49',
            secret='22868ac04ab28a7ae5ec',
            ssl=True,
            port=443
        )

    def create(self, auction, duration):
        """ Creates a new auction channel """
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
        with self.push_lock:
            return self.push.authenticate(
                channel=channel, socket_id=socket
            )
    
    def end(self, auction):
        """ End the current acution """
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
