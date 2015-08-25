from django.conf.urls import patterns, include, url
from django.contrib import admin

import core.views

urlpatterns = patterns(
    '',
    
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    url(r'^pusher_auth$', 'core.views.pusher_auth'),
    url(r'^create/$', 'core.views.create', name='create'),
    url(r'^auction/(?P<auction_id>[0-9]+)/$', 'core.views.auction', name='auction'),
    url(r'^auctions/$', 'core.views.auctions', name='auctions'),
    url(r'^bid/(?P<auction_id>[0-9]+)/$', 'core.views.bid', name='bid'),
    url(r'^items/$', 'core.views.my_items', name='my_items'),
    url(r'^$', 'core.views.home', name='home'),
    
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
)
