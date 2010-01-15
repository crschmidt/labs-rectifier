from ctypes import CDLL, Structure, c_char_p, c_double, c_void_p, c_int, pointer

try:
    libgdal = CDLL("libgdal.so")
except OSError:
    try:
        libgdal = CDLL("libgdal1.so")
    except OSError:
        libgdal = CDLL("libgdal1.4.0.so.1")

libgdal.CPLGetLastErrorMsg.restype = c_char_p
libgdal.GDALCreateGCPTransformer.restype = c_void_p
libgdal.GDALCreateTPSTransformer.restype = c_void_p

class GDALError (Exception):
    def __init__ (self):
        Exception.__init__(self,libgdal.CPLGetLastErrorMsg())

class GCP (Structure):
    _fields_ = (("id",      c_char_p),
                ("info",    c_char_p),
                ("pixel",   c_double),
                ("line",    c_double),
                ("x",       c_double),
                ("y",       c_double),
                ("z",       c_double))

    def __init__ (self, pixel, line, x, y, z = 0.0):
        Structure.__init__(self)
        self.pixel = pixel
        self.line  = line
        self.x     = x
        self.y     = y
        self.z     = 0.0

class GCPTransformer (object):
    """
    >>> gcps = [(4088.91092814, 2763.15406687, 72.8380250931, 19.0290564917), \
                (4258.82959082, 2867.87138224, 72.8398275375, 19.0279205232), \
                (3950.60503992, 3041.74164172, 72.8365015984, 19.0262368413), \
                (258.654269972, 10952.7078168, 72.7933502197, 18.9384386463), \
                (2182.50223829, 3045.2972624,  72.815387249,  19.0257905614), \
                (5544.95430777, 2932.15961155, 72.8551268578, 19.0275553888)]
    >>> g = GCPTransformer(gcps)
    >>> g.transform(((3000,3000),))
    [(72.825369665662336, 19.026545872405777)]
    """

    _create     = libgdal.GDALCreateGCPTransformer
    _destroy    = libgdal.GDALDestroyGCPTransformer
    _transform  = libgdal.GDALGCPTransform

    def __init__ (self, gcps, order = 0):
        gs = ( GCP * len(gcps) )()
        for (n, gcp) in enumerate(gcps):
            gs[n] = GCP(*gcp)
        self.transformer = self._create( len(gcps), gs, order, False )
        if self.transformer is None:
            raise GDALError()

    def __del__ (self):
        if self.transformer:
            self._destroy(self.transformer)

    def transform (self, points, destToSource = False):
        assert self.transformer is not None
        result = pointer(c_int(0))
        xs = (c_double * len(points))()
        for i in range(len(points)): xs[i] = points[i][0]
        ys = (c_double * len(points))()
        for i in range(len(points)): ys[i] = points[i][1]
        zs = (c_double * len(points))()
        for i in range(len(points)): zs[i] = 0.0
        self._transform( self.transformer, int(destToSource),
                         len(points), xs, ys, zs, result )
        if not result[0]: raise GDALError()
        xformed = [(xs[i], ys[i]) for i in range(len(points))]
        return xformed

class TPSTransformer (GCPTransformer):
    """
    >>> gcps = [(4088.91092814, 2763.15406687, 72.8380250931, 19.0290564917), \
                (4258.82959082, 2867.87138224, 72.8398275375, 19.0279205232), \
                (3950.60503992, 3041.74164172, 72.8365015984, 19.0262368413), \
                (258.654269972, 10952.7078168, 72.7933502197, 18.9384386463), \
                (2182.50223829, 3045.2972624,  72.815387249,  19.0257905614), \
                (5544.95430777, 2932.15961155, 72.8551268578, 19.0275553888)]
    >>> t = TPSTransformer(gcps)
    >>> t.transform(((3000,3000),))
    [(72.82530263451811, 19.02654185747901)]
    """
    _create     = libgdal.GDALCreateTPSTransformer
    _destroy    = libgdal.GDALDestroyTPSTransformer
    _transform  = libgdal.GDALTPSTransform

    def __init__ (self, gcps):
        gs = ( GCP * len(gcps) )()
        for n, gcp in enumerate(gcps):
            gs[n] = GCP(*gcp)
        self.transformer = self._create( len(gcps), gs, False )
        if self.transformer is None:
            raise GDALError()

if __name__ == '__main__':
    import doctest
    doctest.testmod()

