from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('httorrent.views',
    # Example:
    # (r'^tutorial_site/', include('tutorial_site.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'(?P<torrent_hash>[0-9a-fA-F]+)/$', 'torrent_detail'),
    (r'^add_torrent/$', 'add_torrent'),
    (r'^ajax_example', 'ajax_example'),
    (r'^$', 'index'),
)
