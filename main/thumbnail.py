import sys
from PIL import Image

def make_thumbnail (filename):
    size = [150,150]
    im = Image.open( filename )
    if im.mode == "L" or im.mode == "P":
        im = im.convert("RGB")
    imsize = im.size
    if imsize[0] > imsize[1]:
      size[1] = int(imsize[0]/float(imsize[1]) * imsize[1])
    else:
      size[0] = int(imsize[1]/float(imsize[0]) * imsize[0])
    im.thumbnail(size)
    im.save("%s.thumbnail.jpg" % (filename))
    return imsize

if __name__ == '__main__':
    for filename in sys.argv[1:]:
        makeThumbnail(filename)

