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

Credits
-------

The MetaCarta Labs Rectifier is available under a Clear BSD license,
from MetaCarta Labs. Copyright 2006-2009.
