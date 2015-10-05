from unittest import TestCase

__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as functions
from lib.python.image_proc import raster_image_math
import json

class TestFunctions(TestCase):

    def test_avg(self):
        input_file=['/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/19990811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20000811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20010811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20020811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20030811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20040811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20050811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20060811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20070811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20080811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20090811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20100811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20110811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20120811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20130811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20140811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif']
        output_file='/data/temp/test/0811_vgt-ndvi_10davg_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        #args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    def test_min(self):
        input_file=['/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/19990811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20000811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20010811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20020811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20030811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20040811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20050811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20060811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20070811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20080811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20090811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20100811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20110811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20120811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20130811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
                    '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi_linearx2/20140811_vgt-ndvi_ndvi_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif']
        output_file='/data/temp/test/0811_vgt-ndvi_10dmin_linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        #args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        raster_image_math.do_min_image(**args)
