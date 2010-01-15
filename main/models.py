from django.db import models

from django.contrib.auth.models import User

import gdal, gdalconst

gdalwarp=False
try: 
    import gdalwarp
except ImportError:
    print "No error estimation support"
    pass
gdalwarp=False

from django.conf import settings

import math

class PublicMaps(models.Manager):
    def get_query_set(self):
        return super(PublicMaps, self).get_query_set().filter(private=False)


class Map(models.Model):
    file = models.FileField(upload_to="maps/")
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    width = models.IntegerField()
    height = models.IntegerField()
    warped = models.CharField(max_length=255, blank=True, null=True)
    warped_width = models.IntegerField(null=True,blank=True)
    warped_height = models.IntegerField(null=True,blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    extent = models.CharField(max_length=255,null=True,blank=True)
    private = models.BooleanField(default=False)
    error = models.FloatField(blank=True, null=True)
    objects = PublicMaps()
    def to_json(obj):
        extent = None
        if obj.extent:
            extent = obj.extent.split(",")
        return {
        'id':             obj.id,
        'filename':       obj.file.name,
        'extent':         extent,
        'width':          obj.width,
        'height':         obj.height,
        'srs':            4326, # obj.srs,
        'warped':         obj.warped,
        'title':          obj.title,
        'description':    obj.description,
        'error':          obj.error,
        'order':          0,
        'gcps':     [(p.lon, p.lat, p.x, p.y, p.err, p.id) for p in obj.gcp_set.all()]
        }

    def set_extent(self):
        root = settings.MEDIA_ROOT
        ds = gdal.Open(str("%s/%s" % (root, self.warped)), gdalconst.GA_ReadOnly)
        xform = ds.GetGeoTransform()
        minx = xform[0]
        maxy = xform[3]
        maxx = minx + ds.RasterXSize * xform[1] + ds.RasterYSize * xform[2]
        miny = maxy + ds.RasterXSize * xform[4] + ds.RasterYSize * xform[5]
        self.warped_width = ds.RasterXSize
        self.warped_height = ds.RasterYSize
        self.extent = "%s, %s, %s, %s" % (minx, miny, maxx, maxy)
        return minx, miny, maxx, maxy
 

    def transform (self, points, dstToSrc = False):
        gcps = [(gcp.x, gcp.y, gcp.lon, gcp.lat) for gcp in self.gcp_set.all()]
        xform = gdalwarp.TPSTransformer(gcps)
        result = xform.transform(points, dstToSrc)
        del xform
        return result
    
    def estimate_error (self):
        if not gdalwarp:
            return 0
        pts = self.gcp_set.all()
        if len(pts) < 3:
            for pt in pts:
                pt.err = 0
            return 0
        invert = [(p.lon, p.lat) for p in pts]
        compare = self.transform(invert, True)
        for n, pt in enumerate(pts):
            dx = pt.x - compare[n][0]
            dy = pt.y - compare[n][1]
            pt.err = dx ** 2 + dy ** 2
            pt.save()
        self.error = math.sqrt( sum([pt.err for pt in pts]) / len(pts) )
        self.save()
        return self.error
    
class GCP(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    lon = models.FloatField()
    lat = models.FloatField()
    map = models.ForeignKey(Map)
    err = models.FloatField(default=0, blank=True, null=True)
