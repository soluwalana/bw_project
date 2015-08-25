from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from models import Bid, Auction
import time

# Create your tests here.

class SimpleTest(TestCase):

    fixtures = ['users.json']
    
    def setUp(self):
        self.client = Client()

    def test_flow(self):
        # First check for the default behavior
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')
        
        response = self.client.get('/login/')
        assert(response.status_code == 200)
        response = self.client.post('/login/?next=/', {'username': 'mimi', 'password': 'mimi'})
        assert(response.status_code == 302)
        assert(response.get('Location') == 'http://testserver/')

        # Test basic responses
        response = self.client.get('/')
        assert(response.status_code == 200)

        response = self.client.get('/create/')
        assert(response.status_code == 200)

        response = self.client.get('/auctions/')
        assert(response.status_code == 200)

        response = self.client.get('/items/')
        assert(response.status_code == 200)

        response = self.client.get('/auction/1/')
        assert(response.status_code == 404)
        
        assert(len(Bid.objects.all()) == 0)
        
        # Create first Item
        response = self.client.post('/create/', {
            'aname': "Test Post", 'adesc': "Some Description", 'aprice': '100.52', 'aduration': 5
        })
        assert(response.status_code == 302)
        assert(response.get('Location') == 'http://testserver/auction/1/')

        response = self.client.get('/auction/1/')
        assert(response.status_code == 200)
        
        #switch user and bid
        response = self.client.get('/logout/')
        print response.status_code
        
        response = self.client.post('/login/?next=/', {'username': 'lili', 'password': 'lili'})
        assert(response.status_code == 302)
        assert(response.get('Location') == 'http://testserver/')
                
        response = self.client.get('/auction/1/')
        assert(response.status_code == 200)

        response = self.client.get('/bid/1/', {})
        assert(response.status_code == 405)

        response = self.client.post('/bid/2/', {})
        assert(response.status_code == 404)

        response = self.client.post('/bid/1/', {
            'bprice': 'hello'
        })
        print 'should be 400', response.status_code
        assert(response.status_code == 400)

        response = self.client.post('/bid/1/', {
            'bprice': '100.2'
        })
        assert(response.status_code == 200)
        assert(response.content == '{"error": "Entered amount is lower than current bid"}')

        response = self.client.post('/bid/1/', {
            'bprice': '105.2'
        })
        assert(response.status_code == 200)
        assert(response.content == '{"success": "You\'re the highest bidder"}')

        assert(len(Auction.objects.all()) == 1)
        assert(len(Bid.objects.all()) == 1)

        response = self.client.get('/auction/1/')
        assert(response.status_code == 200)
        assert('<div class="bid mine">' in response.content)
        assert('<span class="bid_amount">105.2</span>' in response.content)
        time.sleep(5)

        response = self.client.get('/auction/1/')
        assert(response.status_code == 200)
        assert('<span class="won"> Congratulations!! You won this item!! </span>' in response.content)

        response = self.client.get('/items/')
        assert('Test Post </a> purchased for $105.2' in response.content)
        
        response = self.client.get('/logout/')
        assert(response.status_code == 200)
        response = self.client.post('/login/?next=/', {'username': 'mimi', 'password': 'mimi'})
        assert(response.status_code == 302)
        assert(response.get('Location') == 'http://testserver/')

        response = self.client.get('/items/')
        assert(' Test Post </a> was sold for $105.2' in response.content)
        
