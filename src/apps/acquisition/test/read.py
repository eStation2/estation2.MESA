#
#   Test reading/writing datasets for projections in GDAL 3.0.2 (see ES2-535)
#

from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# Import local definitions

from future import standard_library
standard_library.install_aliases()
from shutil import copyfile

# This is a non-georeferenced raster created by pre-proc for LSASAF-HDF5
my_dir = '/data/tmp/ET-Disk/'
orig_file = my_dir+'ET-pre-processed.tif'
input_file = my_dir+'ET-pre-processed-1.tif'
# copyfile(orig_file,input_file)

# Hard-coded definitions
fewsnet_AEA_wkt_new = 'PROJCS["Albers_Conical_Equal_Area",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["standard_parallel_1",-19],PARAMETER["standard_parallel_2",21],PARAMETER["latitude_of_center",1],PARAMETER["longitude_of_center",20],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],AUTHORITY["EPSG","9822"]]'
fewsnet_AEA_mapset = 'FEWSNET-Africa-8km'

lsasaf_disk_wkt_new = 'PROJCS["unnamed",GEOGCS["unnamed ellipse",DATUM["unknown",SPHEROID["unnamed",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Geostationary_Satellite"],PARAMETER["central_meridian",0],PARAMETER["satellite_height",-0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1],AUTHORITY["EPSG","None"]]'
lsasaf_disk_wkt_new_1='PROJCS["Geostationary_Satellite", GEOGCS["GCS_unknown", DATUM["D_unknown", SPHEROID["Spheroid",6378137,298.2572221]],PRIMEM["Greenwich",0], UNIT["Degree",0.017453292519943295]],PROJECTION["Geostationary_Satellite"],PARAMETER["central_meridian",0],PARAMETER["satellite_height",35786023],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["Meter",1]]'

lsasaf_disk_mapset = 'MSG-satellite-3km'

native_mapsetcode = lsasaf_disk_mapset

# Import third-party modules
# from osgeo.gdalconst import *
from osgeo import gdal
from osgeo import osr
from lib.python import mapset
from config import es_constants

# Open the testfile
orig_ds = gdal.Open(input_file, gdal.GF_Write)

# Read Geotags (error ?)
orig_geotransform = orig_ds.GetGeoTransform()
orig_projection = orig_ds.GetProjection()

# Create the Native mapset
native_mapset = mapset.MapSet()
native_mapset.assigndb(native_mapsetcode)

orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())
orig_geo_transform = native_mapset.geo_transform

# Set to original file
orig_ds.SetGeoTransform(native_mapset.geo_transform)
# orig_ds.SetProjection(orig_cs.ExportToWkt())
orig_ds.SetProjection(lsasaf_disk_wkt_new_1)
orig_ds = None

# Read again - to check
new_ds = gdal.Open(input_file)

# Read Geotags (error ?)
new_geotransform = new_ds.GetGeoTransform()
new_projection = new_ds.GetProjection()
wait = 1

# orig_cs = osr.SpatialReference(wkt=native_mapset.spatial_ref.ExportToWkt())
# orig_geo_transform = native_mapset.geo_transform
# orig_size_x = native_mapset.size_x
# orig_size_y = native_mapset.size_y
#
# orig_ds.SetGeoTransform(native_mapset.geo_transform)
# orig_ds.SetProjection(orig_cs.ExportToWkt())
# #
# # Get the Target mapset
# trg_mapset = mapset.MapSet()
# trg_mapset.assigndb('WGS84_Sahel_1km')
# out_cs = trg_mapset.spatial_ref
# out_size_x = trg_mapset.size_x
# out_size_y = trg_mapset.size_y
#
# # Create target in memory
# mem_driver = gdal.GetDriverByName('MEM')
#
# # Assign mapset to dataset in memory
# out_data_type_gdal = 2
# mem_ds = mem_driver.Create('', out_size_x, out_size_y, 1, out_data_type_gdal)
# mem_ds.SetGeoTransform(trg_mapset.geo_transform)
# mem_ds.SetProjection(out_cs.ExportToWkt())

# Do the Re-projection
# orig_wkt = orig_cs.ExportToWkt()
# res = gdal.ReprojectImage(orig_ds, mem_ds, orig_wkt, out_cs.ExportToWkt(),
#                                       es_constants.ES2_OUTFILE_INTERP_METHOD)