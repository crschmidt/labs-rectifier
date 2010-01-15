from django.conf.urls.defaults import *

from django.conf import settings

urlpatterns = patterns('',
    (r'^', include('rectifier.main.urls')),
    (r'^rectifier/', include('rectifier.main.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static/'}),
    (r'^rectifier/static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'static/'}),
    (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^rectifier/uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

)
