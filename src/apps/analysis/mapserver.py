
from config import es_constants
import mapscript

MapserverVersion = mapscript.msGetVersion()
#print MapserverVersion


def getmap():
    productfile = '/data/processing/vgt_ndvi/WGS84_Africa_1km/tif/ndv/20130701_vgt_ndvi_ndv_WGS84_Africa_1km.tif'

    #####   create MAP OBJECT   #####

    # create a new mapfile from scratch
    productmap = mapscript.mapObj(es_constants.template_mapfile)
    #productmap.save('temp.map')
    productmap.setSize(736, 782)
    productmap.setExtent(-4863270.2540311385, -7205400.673576976, 9538688.86734863, 8096680.892889029)
    productmap.units = mapscript.MS_DD
    #productmap.imagecolor.setRGB(255, 255, 255)

    # create a layer for the raster
    layer = mapscript.layerObj(productmap)
    layer.name = 'testlayer'
    layer.type = mapscript.MS_RASTER
    layer.status = mapscript.MS_ON
    layer.data = productfile
    return productmap

