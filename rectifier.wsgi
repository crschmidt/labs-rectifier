#!/usr/bin/python 

import os, sys
dir = os.path.dirname(__file__)
sys.path.append(dir)
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
