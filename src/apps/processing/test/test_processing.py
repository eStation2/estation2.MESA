from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = "Marco Clerici"


from unittest import TestCase
from lib.python import es_logging as log

# Trivial change
logger = log.my_logger(__name__)

from apps.processing import proc_functions
from lib.python import functions
import glob

from lib.python.image_proc.raster_image_math import *

def sst_shapefile_conversion(self, input_file, output_file):

    output_file = functions.list_to_element(output_file)
    # Check if the output file already exists - and delete it
    if os.path.isfile(output_file):
        files=glob.glob(output_file.replace('.shp','.*'))
        for my_file in files:
            os.remove(my_file)

    functions.check_output_dir(os.path.dirname(output_file))
    command=es_constants.es2globals['gdal_polygonize']+' '+ input_file+' '+ output_file+' -nomask -f "ESRI Shapefile"'
    p = os.system(command)

    return 0

class TestProcessing(TestCase):


    def Test_create_permanent_missing_files(self):
        args = {"product_code":"tamsat-rfe", "version":"2.0", "sub_product_code":"10d", "mapset_code":"TAMSAT-Africa-8km"}

        # proc_functions.create_permanently_missing_for_dataset(**args)
        self.assertEqual(1, 1)

    def Test_FrontUtils_so(self):

        infile='/data/processing/modis-sst/v2013.1/MODIS-Africa-4km/tif/sst-day/20150101_modis-sst_sst-day_MODIS-Africa-4km_v2013.1.tif'
        outfile='/data/temp/test.tif'

        do_detect_sst_fronts(input_file=infile, output_file=outfile, input_nodata=None, parameters=None,
                          output_nodata=None, output_format=None, output_type=None, options='')

        # proc_functions.create_permanently_missing_for_dataset(**args)
        self.assertEqual(1, 1)


    def Test_convert_shape(self):

        infile='/data/processing/pml-modis-sst/3.0/SPOTV-IOC-1km/derived/sst-fronts/20160331_pml-modis-sst_sst-fronts_SPOTV-IOC-1km_3.0.tif'
        outfile='/data/temp/20160331_pml-modis-sst_sst-fronts_SPOTV-IOC-1km_3.0.shp'

        status = sst_shapefile_conversion(self,infile,outfile)