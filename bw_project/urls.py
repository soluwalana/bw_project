from django.conf.urls import patterns, include, url
from django.contrib import admin

import core.views

urlpatterns = patterns(
    '',

    # Examples:
    url(r'^$', 'core.views.home', name='home'),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
                       
)
