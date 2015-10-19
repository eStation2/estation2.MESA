from __future__ import absolute_import
__author__ = "Marco Clerici"


from unittest import TestCase
from lib.python import es_logging as log

# Trivial change
logger = log.my_logger(__name__)

from apps.processing import proc_functions
from lib.python.image_proc.raster_image_math import *

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
