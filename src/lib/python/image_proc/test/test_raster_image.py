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
        output_file='/data/temp/test/0811_vgt-ndvi_10davg-linearx2_SPOTV-Africa-1km_sv2-pv2.1.tif'
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

    def test_DIFF(self):
        input_file=['/data/processing/modis-firms/v5.0/SPOTV-Africa-1km/derived/10dcount/20160101_modis-firms_10dcount_SPOTV-Africa-1km_v5.0.tif',\
                    '/data/processing/modis-firms/v5.0/SPOTV-Africa-1km/derived/10dcountavg/0101_modis-firms_10dcountavg_SPOTV-Africa-1km_v5.0.tif']

        output_file='/data/temp/20160101_modis-firms_10dcountdiff_SPOTV-Africa-1km_v5.0.tif'
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",'output_type':'Float32', 'input_nodata':-32767}
        raster_image_math.do_oper_subtraction(**args)

    def test_cumul(self):

        input_files=['/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830301_arc2-rain_1day_ARC2-Africa-11km_2.0.tif',\
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830302_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830303_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830304_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830305_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830306_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830307_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830308_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830309_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', \
                    '/data/processing/arc2-rain/2.0/ARC2-Africa-11km/tif/1day/19830310_arc2-rain_1day_ARC2-Africa-11km_2.0.tif', ]

        output_file='/data/processing/arc2-rain/2.0/ARC2-Africa-11km/derived/10d/19830301_arc2-rain_10d_ARC2-Africa-11km_2.0.tif'

        args = {"input_file": input_files, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",'output_type':'Float32', 'input_nodata':-32767}
        raster_image_math.do_cumulate(**args)

    def test_rain_onset(self):

        input_file = [
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif']

        output_file = '/data/temp/20160911_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif'
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                'output_type': 'Int16', 'input_nodata': -32767, 'current_dekad':2}
        raster_image_math.do_rain_onset(**args)


    def test_rain_onset_1(self):
        input_file = [
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160921_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160911_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/processing/fewsnet-rfe/2.0/FEWSNET-Africa-8km/tif/10d/20160901_fewsnet-rfe_10d_FEWSNET-Africa-8km_2.0.tif', \
            '/data/temp/20160911_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif']

        output_file = '/data/temp/20160921_fewsnet-rfe_rain-onset_FEWSNET-Africa-8km_2.0.tif'
        args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress=lzw",
                'output_type': 'Int16', 'input_nodata': -32767, 'current_dekad':3}
        raster_image_math.do_rain_onset(**args)

    def test_reprojection(self):

        # Define the Native mapset
        native_mapset_name ='SPOTV-SADC-1km'
        target_mapset_name = 'FEWSNET-Africa-8km'

        inputfile='/data/temp/AGRIC_MASK.tif'
        output_file='/data/temp/AGRIC_MASK-'+target_mapset_name+'.tif'

        raster_image_math.do_reproject(inputfile, output_file,native_mapset_name,target_mapset_name)