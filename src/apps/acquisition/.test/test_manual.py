execfile('/srv/www/eStation2/locals.py')
from config.es2 import *
import time
from apps.acquisition import ingestion

# ----------------------------------------------------------------------------------
# Definitions for MSG
# ----------------------------------------------------------------------------------
inputFiles=(test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000001___-201309040800-__',
test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000002___-201309040800-__',
test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000003___-201309040800-__',
test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-000004___-201309040800-__',
test_data_dir_in+'L-000-MSG3__-MPEF________-MPEG_____-PRO______-201309040800-__')

out_file = './201309040800_MSG_MPE_MPE_native.tif'

product = 'MSG_MPE'
sprod1 = {'subproduct': 'MPE', 'zip_expr': 'MPE'}
subproducts = (sprod1, 0)

# Note: the grib can be managed by python-gdal already !
#tmp_grib_file=ingestion.compose_regions('MPE', inputFiles, out_file, 'segments')


# Call ingestion routine: 1- MPE, no reprojection
#ingestion.ingest_file(tmp_grib_file, out_file, product, subproducts, mapset='',unzip='')

# Call ingestion routine: 2- MPE, reprojection to VGT
cl=MapSet()
cl.assign_vgt4africa()
out_file = './201309040800_MSG_MPE_MPE_vgt4africa.tif'
#ingestion.ingest_file(tmp_grib_file, out_file, product, subproducts, mapset=cl,unzip='')

# ----------------------------------------------------------------------------------
# Definitions for VGT
# ----------------------------------------------------------------------------------
# Definitions
in_filename = 'V2KRNS10__20130701_NDVI__Africa.ZIP'        # It actually ingests 2 datasets (NDV/SM)!
out_file = './20130701_VGT_NDVI_NDV_WGS84_Africa_1km.tif'
in_file = test_data_dir_in + in_filename

product = 'VGT_NDVI'
sprod1 = {'subproduct': 'NDV', 'zip_expr': 'NDV'}
sprod2 = {'subproduct': 'SM', 'zip_expr': 'SM'}

subproducts = (sprod1, sprod2, 0)

# Native mapset (file not geo-referenced)
native_mapset = MapSet()
native_mapset.assign_vgt4africa()

# Call ingestion routine: 3- NDVI, no reprojection
#ingestion.ingest_file(in_file, out_file, product, subproducts, '', native_mapset=native_mapset,
 #                                unzip='zip')

# Call ingestion routine: 2- MPE, reprojection to VGT
cl=MapSet()
cl.assign_ecowas()
out_file = './20130701_VGT_NDVI_NDV_WGS84_ECOWAS_1km.tif'
ingestion.ingest_file(in_file, out_file, product, subproducts, mapset=cl, native_mapset=native_mapset, unzip='zip')

