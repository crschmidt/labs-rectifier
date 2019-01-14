MetaCarta Labs Rectifier
========================

The MetaCarta Labs Rectifier is a Django-based server and 
OpenLayers-based client which allows you to upload maps, 
and transform them to match the real world.

To setup:

 * Install Django
 * Install PIL
 * Install GDAL and MapServer, with Python bindings
   * Make sure gdalinfo, gdal_translate, etc. are on the default path.

Then:
 
  * Edit paths at the top of settings.py
  * Edit the paths at the top of warpviavrt.sh to match
  * python manage.py syncdb
  * python manage.py runserver

Notes in 2019
-------------

This application was tested (in 2019) to run on Django 1.1. (Yes, that's
1.1, not 1.10.) I know this is ancient. There are no immediate plans to
update this support. The approximate setup steps above should still
work, though some steps were left out -- e.g. you also need to install
simplejson.

For 2019, approximate steps for installation on an Ubuntu 18.04 LTS
installation:

   apt install sqlite3 cgi-mapserver python-mapscript python-gdal \
               python-pil virtualenv gdal-bin
   git clone https://github.com/crschmidt/labs-rectifier rectifier
   cd rectifier
   virtualenv env --system-site-packages 
   # needed because you need the Ubuntu python-gdal installation, not
   # one you install via PIL, due to version mismatches.
   source env/bin/activate
   pip install Django==1.1.4
   mkdir db/
   python manage.py syncdb
   python manage.py runserver 0.0.0.0 8000

I should note that in reviewing this software, the call out to
scripts/warpviavrt.sh seems dangerous to 2019-me. It's possible that
this is safe, but I would recommend convincing yourself that there's no
shell escape possibilities here before running on a server that you
think might matter.

Credits
-------

The MetaCarta Labs Rectifier is available under a Clear BSD license,
from MetaCarta Labs. Copyright 2006-2009.
