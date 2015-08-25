from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse

from django.db import IntegrityError, transaction
from django.db.models.aggregates import Max
from django.db.models import F

from apps import AUCTIONEER
from models import Auction, Bid
from datetime import timedelta, datetime
import pusher, pytz, re
    
## Views

@login_required(login_url='/login/')
def home(request):
    """ This function will display your options for bidding and creating new bids """
    return render(request, 'index.html')

@login_required(login_url='/login/')
def create(request):
    """ This function will display your creat page for new auctions """
    if request.method == 'GET':
        return render(request, 'create.html')

    if request.method == 'POST':
        
        try:
            duration = request.POST.get('aduration')

            auction = Auction()
            auction.item_name = request.POST.get('aname')
            auction.description = request.POST.get('adesc')
            auction.list_price = price_to_cents(request.POST.get('aprice'))
            auction.cur_price = auction.list_price
            auction.owner = request.user
            auction.expires = duration_to_datetime(duration)
            auction.save()
            AUCTIONEER.create(auction, float(duration))
            
            return HttpResponseRedirect(reverse('auction', args=(auction.id,)))

        except (TypeError, ValueError) as err:
            print err
            return render(request, 'create.html', {
                'error_message': 'Invalid input types for parameters'
            })

        except IntegrityError as err:
            print err
            return render(request, 'create.html', {
                'error_message': 'You have already created an Auction by that name'
            })

    return HttpResponse(status=500)


@login_required(login_url='/login/')
def auction(request, auction_id):
    """ Displays the auction page """

    if request.method != 'GET':
        return HttpResponse('GET only for this page', status=405)
        
    auctions = Auction.objects.filter(id=auction_id)
    if len(auctions) == 0:
        raise Http404("That Auction doesn't exist")

    auction = auctions[0]

    ended = pytz.utc.localize(datetime.now()) > auction.expires
    
    bids = Bid.objects.filter(auction=auction).order_by('-bid_time')
    max_bid = bids[0] if len(bids) > 0 else None

    return render(request, 'auction.html', {
        'auction': auction,
        'bids': bids,
        'max_bid': max_bid,
        'ended': ended,
        'user_id': request.user.id,
        'push_key': AUCTIONEER.key
    })

@login_required(login_url='/login/')
def auctions(request):
    """ Display a list of current auctions """
    now = pytz.utc.localize(datetime.now())
    available = Auction.objects.filter(expires__gt=now)
    return render(request, 'auctions.html', {
        'available': available,
        'push_key': AUCTIONEER.key
    })
    
@login_required(login_url='/login/')
def my_items(request):
    now = pytz.utc.localize(datetime.now())
    
    sold = Auction.objects.filter(owner=request.user, expires__lt=now)
    selling = Auction.objects.filter(owner=request.user, expires__gt=now)
    wbids = Bid.objects.values('auction').filter(
        bidder=request.user, bid_amount=F('auction__cur_price'), auction__expires__lt=now
    )

    wids = set([wbid['auction'] for wbid in wbids])
    auctions_won = Auction.objects.filter(pk__in=wids)
        
    obids = Bid.objects.values('auction').filter(bidder=request.user, auction__expires__gt=now)
    oids = set([obid['auction'] for obid in obids])
    bid_on = Auction.objects.filter(pk__in=oids)
        
    return render(request, 'items.html', {
        'sold': sold,
        'selling': selling,
        'won': auctions_won,
        'bidding': bid_on,
        'push_key': AUCTIONEER.key
    })
    
## JSON API 
    
@login_required(login_url='/login/')
def bid(request, auction_id):
    """ Allows a user to bid on a particular item """

    if request.method != 'POST':
        return JsonResponse({'error': 'Must be called with post'}, status=405)

    auctions = Auction.objects.filter(id=auction_id)
    if len(auctions) == 0:
        return JsonResponse({'error': 'That auction does not exist'}, status=404)
        
    auction = auctions[0]

    if pytz.utc.localize(datetime.now()) > auction.expires:
        return JsonResponse({'error': 'This auction has ended'})
    
    try:
        bid_amount = price_to_cents(request.POST.get('bprice'))
    except (TypeError, ValueError) as err:
        print err
        return JsonResponse({'error': "Invalid input for bid amount"}, status=400)
    
    try:
        with transaction.atomic():
            bids = Bid.objects.filter(auction=auction).order_by('-bid_amount')

            if (len(bids) > 0 and bids[0].bid_amount >= bid_amount) or (auction.list_price > bid_amount):
                return JsonResponse({'error': "Entered amount is lower than current bid"})

            bid = Bid()
            bid.bidder = request.user
            bid.auction = auction
            bid.bid_amount = bid_amount
            bid.save()

            auction.cur_price = bid_amount
            auction.save()
            AUCTIONEER.bid(auction, bid)

    except IntegrityError as err:
        print err
        return JsonResponse({'error': "You've already been outbid"})
        
    return JsonResponse({'success': "You're the highest bidder"})


@csrf_exempt
def pusher_auth(request):
    """ This function is the authentication end point for the pusher stream """
    if not request.user.is_authenticated():
        return JsonResponse({'error': 'Not Authenticated for this stream'}, status=404)
        
    if not request.POST.get('channel_name') or not request.POST.get('socket_id'):
        return JsonResponse({'error': 'Incorrect parameters for authentication'}, status=404)

    auth = AUCTIONEER.authenticate(
        request.POST.get('channel_name'),
        request.POST.get('socket_id')
    )
    return JsonResponse(auth)
    
        
## Helper functions

def price_to_cents(price):
    """ returns the given dollar amount and returns the value in cents
        to avoid dealing with money values as floats which causes numerical
        issues """
    if not re.match('^\d+(\.\d{1,2})?$', price.strip()):
        raise ValueError
    return int(float(price) * 100)

def duration_to_datetime(duration):
    """ Convert duration in seconds to a time in the future (expiration) in UTC """
    expires = datetime.now() + timedelta(seconds=float(duration))
    return pytz.utc.localize(expires)

