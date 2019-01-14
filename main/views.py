from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from django.conf import settings

from main.models import Map, GCP
from main.helpers import json_exception, json_response

from thumbnail import make_thumbnail

import os, time

@json_exception
def warp(request, id):
    map = Map.objects.get(pk=id)
    order = 1
    map_name = os.path.basename(map.file.path) 
    target = "%s-%s.tif" % (map_name, time.time())
    os.system("%s/scripts/warpviavrt.sh %s %s %s" % (settings.BASE_PATH, map_name, target, order))
    final_path = "%s/%s" % (settings.MAP_PATH, target) 
    if os.access(final_path, os.R_OK):
        if map.warped:
            try: 
                os.unlink(map.warped)
            except OSError:
                pass
        map.warped = "%s/%s" % (settings.MAP_DIRNAME, target)
        map.set_extent()
        map.save()
    return json_response(request, map) 

@json_exception
def add_gcp(request, id):
    map = Map.objects.get(pk=id)
    if 'gcp' in request.GET:
        gcp = GCP.objects.get(pk=request.GET['gcp'])
    else:
        gcp = GCP(map=map)

    for field in ('lon', 'lat', 'x', 'y'):
        setattr(gcp, field, request.GET[field])
    gcp.save()    
    map.estimate_error()
    return json_response(request, map) 

@json_exception
def delete_gcp(request, id):
    gcp = GCP.objects.get(pk=request.GET['gcp'])
    gcp.delete()
    map = Map.objects.get(pk=id)
    map.estimate_error()
    return json_response(request, map)

def catalog(request):
    maps = Map.objects.all().order_by("-id")
    return render_to_response("catalog.html", {'maps':maps[0:50]})

def map(request, id):
    map = Map.objects.get(pk=id)
    return render_to_response("map.html", {'map':map})

def rectify(request):
    return render_to_response("rectify.html")

def faq(request):
    return render_to_response("faq.html")

def map_info(request, id):
    map = Map.objects.get(pk=id)
    return json_response(request, map)

@json_exception
def map_list(request):
    maps = Map.objects.filter(private=False)
    maplist = {}
    for obj in maps:
        maplist[obj.id] = obj.to_json() 

    return json_response(request, maplist)

def wms(request):
    import mapscript
    image = None
    for field in ['IMAGE', 'COVERAGE', 'image', 'coverage', 'id', 'ID']:
        if field in request.GET: image = request.GET[field] 
    try:
        image = int(image)
        obj = Map.objects.get(pk=image)
        filename = obj.warped
    except:
        filename = "%s" % image 
    filename = "%s/%s" % (settings.MAP_PATH, os.path.basename(filename))    
    ows = mapscript.OWSRequest()
    for k, v in request.GET.items():
        if k.lower() in ['image', 'coverage']: continue 
        ows.setParameter(k, v)
    ows.setParameter("LAYERS", "image")
    ows.setParameter("COVERAGE", "image")
    map = mapscript.mapObj('%s/wms.map' % settings.BASE_PATH)
    raster = mapscript.layerObj(map)
    raster.name = 'image'
    raster.type = mapscript.MS_LAYER_RASTER
    raster.data = filename 
    raster.status = mapscript.MS_DEFAULT
    raster.setProjection( "+init=epsg:4326" )
    raster.dump = mapscript.MS_TRUE
    mapscript.msIO_installStdoutToBuffer()
    contents = map.OWSDispatch(ows)
    content_type = mapscript.msIO_stripStdoutBufferContentType()
    content = mapscript.msIO_getStdoutBufferBytes()
    return HttpResponse(content, content_type = content_type)

def upload(request):
    if 'file' in request.FILES:
        file = request.FILES['file']
        title = request.POST.get("title", "Untitled")
        description = request.POST.get("description", None)
        user = request.user
        if not user.id:
            user = None
        m = Map(title=title, description=description, width=0, height=0, user=user)
        m.file.save(file.name, file)
        im = make_thumbnail(m.file.path)
        m.width = im[0]
        m.height = im[1]
        m.save()
        return HttpResponseRedirect("/rectifier/rectify/%s" % m.id)
