from django.conf.urls.defaults import *

urlpatterns = patterns('main.views',
    (r'^$', 'catalog'),
    (r'^map/(?P<id>[0-9]*)$', 'map'),
    (r'^faq$', 'faq'),
    (r'^wms.cgi', 'wms'),
    (r'^upload.cgi', 'upload'),
    (r'^rectify/[0-9]*', 'rectify'),
    (r'^api.cgi/info/(?P<id>[0-9]*)', 'map_info'),
    (r'^api.cgi/add/(?P<id>[0-9]*)', 'add_gcp'),
    (r'^api.cgi/delete/(?P<id>[0-9]*)', 'delete_gcp'),
    (r'^api.cgi/warp/(?P<id>[0-9]*)', 'warp')
)    
