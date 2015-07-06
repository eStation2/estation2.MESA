# Import local definitions
import locals

outputfile='test.tif'
dir='/tmp/eStation2/test_files/'
# Tif Georeff
file='chlor_a_merged.tif'
# HDF4 non-georef
file='0001_NDV.HDF'

# Import third-party modules
from osgeo.gdalconst import *
from osgeo import gdal
from osgeo import osr
from lib.python import mapset
from config import es_constants

# Open the file
orig_ds=gdal.Open(dir+file)

# Get the Native mapset
native_mapset = mapset.MapSet()
native_mapset.assigndb('WGS84_Africa_1km')

orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())
orig_geo_transform = native_mapset.geo_transform
orig_size_x = native_mapset.size_x
orig_size_y = native_mapset.size_y

orig_ds.SetGeoTransform(native_mapset.geo_transform)
orig_ds.SetProjection(orig_cs.ExportToWkt())

# Get the Target mapset
trg_mapset = mapset.MapSet()
trg_mapset.assigndb('WGS84_Sahel_1km')
out_cs = trg_mapset.spatial_ref
out_size_x = trg_mapset.size_x
out_size_y = trg_mapset.size_y

# Create target in memory
mem_driver = gdal.GetDriverByName('MEM')

# Assign mapset to dataset in memory
out_data_type_gdal=2
mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)
mem_ds.SetGeoTransform(trg_mapset.geo_transform)
mem_ds.SetProjection(out_cs.ExportToWkt())

# Do the Re-projection
orig_wkt =  orig_cs.ExportToWkt()
res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
                                      es_constants.ES2_OUTFILE_INTERP_METHOD)