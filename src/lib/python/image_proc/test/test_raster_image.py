from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase
import unittest
__author__ = "Jurriaan van 't Klooster"

import lib.python.functions as functions
from lib.python.image_proc import raster_image_math
import json
import os, shutil, tempfile

class TestRasterImage(unittest.TestCase):

    def test_avg(self):
        # input_file=['/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/19990811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20000811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20010811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20020811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20030811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20040811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20050811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20060811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20070811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20080811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20090811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20100811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20110811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20120811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20130811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20140811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif']
        input_file=['/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180801_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181011_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181021_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180821_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181101_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180901_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181111_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180911_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181121_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180921_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181201_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181001_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        output_file='/data/tmp/0811_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        #args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_avg_image(**args)

    def test_min(self):
        # input_file=['/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/19990811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20000811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20010811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20020811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20030811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20040811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20050811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20060811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20070811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20080811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20090811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20100811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20110811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20120811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20130811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/ndvi-linearx2/20140811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif']
        input_file=['/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180801_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181011_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181021_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180821_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181101_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180901_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181111_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180911_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181121_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180921_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181201_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181001_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        output_file='/data/tmp/0811_vgt-ndvi_10dmin-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        #args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        raster_image_math.do_min_image(**args)

    def test_perc_diff(self):
        input_file=['/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/linearx2diff-linearx2/20181201_vgt-ndvi_linearx2diff-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10dstd-linearx2/1201_vgt-ndvi_10dstd-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        output_file='/data/tmp/20181201_vgt-ndvi_10dsndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        #args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_division_perc(**args)

    def test_std(self):
        # input_file=['/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/19990511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20000511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20010511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20020511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20030511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20040511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20050511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20060511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20070511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20080511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20090511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20100511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20110511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20120511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20130511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20140511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20150511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20160511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',\
        #             '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20170511_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        #
        #
        # output_file='/data/temp/test/0511_vgt-ndvi_10dstd-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        # avg_file='/data/temp/test/0511_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

        input_file=['/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180801_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181011_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181021_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180821_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181101_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180901_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181111_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180911_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181121_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180921_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181201_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181001_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        output_file='/data/tmp/0811_vgt-ndvi_10dstd-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        avg_file='/data/tmp/0811_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        # args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", "input_nodata":-32768}
        args = {"input_file": input_file, "avg_file": avg_file, "output_format": 'GTIFF', "options": "compress=lzw", "output_stddev": output_file}
        raster_image_math.do_stddev_image(**args)
        self.assertEqual(1, 1)


    def test_DIFF(self):
        input_file=['/data/processing/modis-firms/v6.0/SPOTV-Africa-1km/derived/10dcount/20160101_modis-firms_10dcount_SPOTV-Africa-1km_v6.0.tif',\
                    '/data/processing/modis-firms/v6.0/SPOTV-Africa-1km/derived/10dcountavg/0101_modis-firms_10dcountavg_SPOTV-Africa-1km_v6.0.tif']

        output_file='/data/tmp/20160101_modis-firms_10dcountdiff_SPOTV-Africa-1km_v6.0.tif'
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",'output_type':'Float32', 'input_nodata':-32767}
        raster_image_math.do_oper_subtraction(**args)
        self.assertEqual(1, 1)
    def test_baresoil(self):

        # Create baresoil mask for 2016/12/21 (w/o using delta_ndvi_max .. only ndvi_max)

        input_file='/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20161221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        min_file  = '/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/10dmin-linearx2/1221_vgt-ndvi_10dmin-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        max_file  = '/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/derived/10dmax-linearx2/1221_vgt-ndvi_10dmax-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
        min_file  = ''
        max_file  = ''

        output_file='/data/tmp/20161221_vgt-ndvi_baresoil-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'

        args = {"input_file": input_file, "min_file": min_file, "max_file": max_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_baresoil(**args)
        self.assertEqual(1, 1)
    def test_ratio(self):

        # Create ratio_linearx2 for 2016/12/21

        input_file='/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20161221_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        avg_file  = '/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10davg-linearx2/1221_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file='/data/tmp/20161221_vgt-ndvi_ratio-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

        args = {"input_file": [input_file,avg_file], "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_oper_division_perc(**args)

        # Use baresoil mask to filter out desert/bare areas

        output_file_masked='/data/tmp/20161221_vgt-ndvi_ratio-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        mask = '/data/tmp/20161221_vgt-ndvi_baresoil-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        args = {"input_file": output_file, "mask_file": mask, "output_file":output_file_masked, "options":"compress = lzw" , "mask_value":-32768, "out_value": -32768}
        raster_image_math.do_mask_image(**args)
        self.assertEqual(1, 1)

    def test_vci(self):

        input_file='/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/tif/ndv/20170301_vgt-ndvi_ndv_SPOTV-Africa-1km_sv2-pv2.2.tif'
        min_file  = '/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10dmin-linearx2/0301_vgt-ndvi_10dmin-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        max_file  = '/data/processing/vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/10dmax-linearx2/0301_vgt-ndvi_10dmax-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

        output_file='/data/tmp/20170301_vgt-ndvi_baresoil-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'

        args = {"input_file": input_file, "min_file": min_file, "max_file": max_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw"}
        raster_image_math.do_make_vci(**args)
        self.assertEqual(1, 1)

    def test_cumul(self):

        # input_files=['/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830301_arc2-rain_1day_ARC2-Africa-11km_2.0.tif',\
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830302_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830303_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830304_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830305_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830306_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830307_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830308_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830309_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
        #             '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830310_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', ]
        input_files=['/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180801_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181011_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180811_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181021_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180821_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181101_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180901_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181111_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180911_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181121_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20180921_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181201_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif',
                    '/data/processing//vgt-ndvi/sv2-pv2.2/SPOTV-Africa-1km/derived/ndvi-linearx2/20181001_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif']
        # output_file='/data/processing/arc2-rain/2.0/ARC2-Africa-11km/derived/10d/19830301_arc2-rain_10d_ARC2-Africa-11km_2.0.tif'
        output_file = '/data/tmp/20180001_vgt-ndvi_ndvi-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        args = {"input_file": input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",'output_type':'Float32', 'input_nodata':-32767}
        raster_image_math.do_cumulate(**args)
        self.assertEqual(1, 1)
    def test_rain_onset(self):

        input_file = [
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif']

        output_file = '/data/tmp/20160911_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif'
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                'output_type': 'Int16', 'input_nodata': -32767, 'current_dekad':2}
        raster_image_math.do_rain_onset(**args)
        self.assertEqual(1, 1)

    def test_rain_onset_1(self):
        input_file = [
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160921_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/tmp/20160911_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif']

        output_file = '/data/tmp/20160921_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif'
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                'output_type': 'Int16', 'input_nodata': -32767, 'current_dekad':3}
        raster_image_math.do_rain_onset(**args)
        self.assertEqual(1, 1)
    def test_reprojection(self):

        # Define the Native mapset
        native_mapset_name ='SPOTV-SADC-1km'
        target_mapset_name = 'FEWSNET-Africa-8km'

        inputfile='/data/tmp/20161221_vgt-ndvi_ratio-linearx2_SPOTV-Africa-1km_sv2-pv2.2.tif'
        output_file='/data/tmp/AGRIC_MASK-'+target_mapset_name+'.tif'

        raster_image_math.do_reproject(inputfile, output_file,native_mapset_name,target_mapset_name)
        self.assertEqual(1, 1)

    # # Didnt work
    # def test_stats_4_raster(self):
    #
    #     # Define the Native mapset
    #     input_mapset_name ='SPOTV-Africa-1km'
    #     grid_mapset_name = 'SPOTV-Africa-1km'
    #     target_mapset_name='SPOTV-Africa-10km'
    #     grid_file='/eStation2/layers/Mask_Africa_SPOTV_10km.tif'
    #
    #
    #     input_file='/data/processing/modis-firms/v6.0/SPOTV-Africa-1km/derived/10dcount/20171101_modis-firms_10dcount_SPOTV-Africa-1km_v6.0.tif'
    #     output_file='/data/tmp/20171101_modis-firms_10dcount10k_SPOTV-Africa-1km_v6.0.tif'
    #     tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
    #                               dir='/data/tmp/')
    #
    #     # Temporary (not masked) file
    #     output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)
    #
    #     operation='sum'
    #
    #     raster_image_math.do_stats_4_raster(input_file, grid_file, output_file_temp, operation, input_mapset_name, grid_mapset_name,
    #                                         output_format=None, nodata=-32768, output_type= 'Int16',options=None )
    #
    #     args = {"inputfile": output_file_temp, "output_file": output_file, "native_mapset_name": grid_mapset_name,
    #             "target_mapset_name": target_mapset_name}
    #
    #     raster_image_math.do_reproject(**args)
    #     self.assertEqual(1, 1)
    # Dint test
    # def test_create_surface_area_raster(self):
    #
    #     # Define the Native mapset
    #     input_mapset_name ='SPOTV-Africa-1km'
    #     grid_mapset_name = 'SPOTV-Africa-1km'
    #     target_mapset_name='SPOTV-Africa-1km'
    #     #grid_file='/eStation2/layers/Mask_Africa_SPOTV_10km.tif'
    #
    #
    #     input_file='/data/processing/exchange/area/area_calc.tif'
    #     output_file='/data/processing/exchange/area/surface_area_SpotAfrica1km_with_equator.tif'
    #     tmpdir = tempfile.mkdtemp(prefix=__name__, suffix='_' + os.path.basename(output_file),
    #                               dir='/data/processing/exchange/')
    #
    #     # Temporary (not masked) file
    #     output_file_temp = tmpdir+os.path.sep+os.path.basename(output_file)
    #
    #     operation='sum'
    #
    #     raster_image_math.create_surface_area_raster(output_file=output_file_temp, output_type='Float32',
    #                                                  mapsetcode=grid_mapset_name)
    #
    #     args = {"inputfile": output_file_temp, "output_file": output_file, "native_mapset_name": grid_mapset_name,
    #              "target_mapset_name": target_mapset_name}
    #     #
    #     raster_image_math.do_reproject(**args)
    #     self.assertEqual(1, 1)

    # Didnt work
    # def test_sst_fronts(self):
    #     input_file = '/data/processing/modis-sst/v2013.1/MODIS-Africa-4km/tif/sst-day/20181007_modis-sst_sst-day_MODIS-Africa-4km_v2013.1.tif'
    #
    #     output_file = '/data/tmp/20160921_modis-sst_sst-fronts_MODIS-Africa-4km_v2013.1.tif'
    #
    #     # prod == 'modis-sst'
    #     parameters = {'histogramWindowStride': 8,  # smaller window detects more fronts
    #                   'histogramWindowSize': 32,
    #                   'minTheta': 0.76,
    #                   # 'minPopProp': 0.25,
    #                   'minPopMeanDifference': 25,  # Temperature: 0.45 deg (multiply by 100 !!)
    #                   'minSinglePopCohesion': 0.60,
    #                   'minImageValue': 1,
    #                   'minThreshold': 1}
    #
    #
    #     args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
    #             "parameters": parameters}
    #     raster_image_math.do_detect_sst_fronts(**args)
    #     self.assertEqual(1, 1)

    def test_compute_primary_production(self):
        input_file = [
            '/data/processing/modis-chla/v2013.1/MODIS-Africa-4km/tif/chla-day/20181007_modis-chla_chla-day_MODIS-Africa-4km_v2013.1.tif', \
            '/data/processing/modis-sst/v2013.1/MODIS-Africa-4km/tif/sst-day/20181007_modis-sst_sst-day_MODIS-Africa-4km_v2013.1.tif', \
            '/data/processing/modis-kd490/v2012.0/MODIS-Africa-4km/tif/kd490-day/20181007_modis-kd490_kd490-day_MODIS-Africa-4km_v2012.0.tif', \
            '/data/processing/modis-par/v2012.0/MODIS-Africa-4km/tif/par-day/20181007_modis-par_par-day_MODIS-Africa-4km_v2012.0.tif']
        output_file = '/data/tmp/20181007_modis-pp_monavg_MODIS-Africa-4km_v2013.1.tif'

        # prod == 'modis-sst'
        parameters = {'histogramWindowStride': 8,  # smaller window detects more fronts
                      'histogramWindowSize': 32,
                      'minTheta': 0.76,
                      # 'minPopProp': 0.25,
                      'minPopMeanDifference': 25,  # Temperature: 0.45 deg (multiply by 100 !!)
                      'minSinglePopCohesion': 0.60,
                      'minImageValue': 1,
                      'minThreshold': 1}

        args = {"chla_file": input_file[1], "sst_file": input_file[3], "kd_file": input_file[0],
                "par_file": input_file[2], \
                "sst_nodata": 0, "kd_nodata": 0, "chla_nodata": 0, \
                "par_nodata": 0, "output_file": output_file, "output_nodata": -32768,
                "output_format": 'GTIFF', \
                "output_type": None, "options": "compress=lzw"}
        raster_image_math.do_compute_primary_production(**args)
        self.assertEqual(1, 1)

    def test_compute_opFish_indicator(self):
        input_file = '/data/processing/modis-chla/v2013.1/MODIS-Africa-4km/tif/chla-day/20181007_modis-chla_chla-day_MODIS-Africa-4km_v2013.1.tif'

        output_file = '/data/tmp/20181007_modis-chla_opfish_MODIS-Africa-4km_v2013.1.tif'

        # prod == 'modis-chla':
        parameters = {'chl_grad_min': 0.00032131,  # smaller window detects more fronts
                      'chl_grad_int': 0.021107,
                      'chl_feed_min': 0.08,
                      'chl_feed_max': 11.0,  # Temperature: 0.45 deg (multiply by 100 !!)
                      'dc': 0.91}

        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                "parameters": parameters}
        raster_image_math.compute_opFish_indicator(**args)
        self.assertEqual(1, 1)

suite_raster_image = unittest.TestLoader().loadTestsFromTestCase(TestRasterImage)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_raster_image)