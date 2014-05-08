execfile('/srv/www/eStation2/locals.py')
from config.es2 import *

#file='/srv/www/eStation2/apps/acquisition/.test/S-LSA_-HDF5_LSASAF_MSG_LST_NAfr_201402251200'
#file='/tmp/eStation2/apps.acquisition.ingestionfspKq5_L-000-MSG3__-MPEF________-MPEG_____-000001___-201309040800-__/MSG_MPE_grib_temp.grb'
outputfile='test.tif'
#file='/tmp/eStation2/apps.acquisition.ingestion8g6VWN_MCD45monthly.A2005274.Win14.005.burndate.tif.gz/burndate_merged.tif'
file='/tmp/eStation2/apps.acquisition.ingestionLGeAPh_PML_NEMadagascar_MODIS_oc_3daycomp_20100802_20100804.nc.bz2/PML_NEMadagascar_MODIS_oc_3daycomp_20100802_20100804.nc'

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
