# Import local definitions
import locals

outputfile='test.tif'
file=locals.es2globals['data_dir']+'tmp/PML_EMadagascar_MODIS_oc_3daycomp_20100802_20100804.nc'

# Import third-party modules
from osgeo.gdalconst import *
from osgeo import gdal
from osgeo import osr

# By using pygrib

#grbs = pygrib.open(file)
#grb = grbs.select(name='Instantaneous rain rate')[0]
#values = grb.values

#print values.shape
#print values[2200,1600]*3600.

# By using GDAL -> reads values as 0.0 !!!!!!
ds=gdal.Open(file)
orig_cs=osr.SpatialReference()
orig_cs.ImportFromWkt(ds.GetProjectionRef())
orig_geo_transform = ds.GetGeoTransform()
orig_size_x = ds.RasterXSize
orig_size_y = ds.RasterYSize

print orig_geo_transform
print orig_size_x

