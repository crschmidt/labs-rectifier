import simplejson
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

import sys, traceback
import django.conf

class ApplicationError(Exception): pass

def json_exception(func):
    """Wrap up a view, and return a json error with any exceptions""" 
    def wrap(request, *args, **kw):
        try:
            return func(request, *args, **kw)

        except ObjectDoesNotExist, E:
            return generate_error_response(E, format="json", request=request, status_code=404)

        except Http404, E:
            return generate_error_response(E, format="json", request=request, status_code=404)

        except ApplicationError, E:
            return generate_error_response(E, format="json", request=request)

        except Exception, E:
            return generate_error_response(E, format="json", request=request, unexpected=True)
    return wrap

def json_response(request, obj):
    """Take an object. If the object has a to_json method, call it, 
       and take either the result or the original object and serialize
       it using simplejson. If a callbakc was sent with the http_request,
       wrap the response up in that and return it, otherwise, just return
       it."""
    if hasattr(obj, 'to_json'):
        obj = obj.to_json()
    if request.GET.has_key('_sqldebug'):
        import django.db
        obj['sql'] = django.db.connection.queries
    data = simplejson.dumps(obj)
    if request.GET.has_key('callback'):
        data = "%s(%s);" % (request.GET['callback'], data)
    elif request.GET.has_key('handler'):
        data = "%s(%s);" % (request.GET['handler'], data)

    return HttpResponse(data)

def generate_error_response(exception, format="text", status_code=None, request=None, unexpected=False):
    """Generate an error response, used in textexception/jsonexception
       decorators.
       
       >>> try:
       ...     int('a')
       ... except Exception, E:
       ...    response = generate_error_response(E) 
       >>> response.status_code 
       500
       >>> response.content.find("Error Type: ValueError")
       0
       
       >>> try:
       ...     raise ApplicationError("Failed")
       ... except ApplicationError, E:
       ...    response = generate_error_response(E) 
       >>> response.status_code
       200
       >>> "Error: Failed" in response.content
       True

       >>> try:
       ...     raise ApplicationError("Failed")
       ... except ApplicationError, E:
       ...    h = HttpRequest()
       ...    response = generate_error_response(E, format='json', request=h)
       >>> data = simplejson.loads(response.content)
       >>> data['error']
       u'Failed'
       
    """
    
    type = sys.exc_type.__name__
    error = {'error': str(exception), 'type': type, 'unexpected':unexpected}
    if django.conf.settings.DEBUG and unexpected:
        error['traceback'] = traceback.format_exc()
   
    if format == "json" and request:
        response = json_response(request, error)
    else:
        response = text_error_response(error)
   
    if hasattr(exception, "status_code"):
        response.status_code = exception.status_code
    elif status_code:
        response.status_code = status_code
    else:
        response.status_code = 500

    return response

