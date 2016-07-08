from __future__ import absolute_import
__author__ = "Jurriaan van 't Klooster"

from lib.python.image_proc import raster_image_math


def test_avg():
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

def test_min():
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

def test_avg_firms():

    input_file=['/data/processing/modis-firms/v5.0/SPOTV-Africa-1km/derived/10dcount/20150101_modis-firms_10dcount_SPOTV-Africa-1km_v5.0.tif',\
                '/data/processing/modis-firms/v5.0/SPOTV-Africa-1km/derived/10dcount/20160101_modis-firms_10dcount_SPOTV-Africa-1km_v5.0.tif']

    output_file='/data/temp/0101_modis-firms_10dcountavg_SPOTV-Africa-1km_v5.0.tif'
    args = {"input_file": input_file, "output_file": output_file, "output_format": 'GTIFF', "options": "compress = lzw", 'output_type':'Float32', 'input_nodata':-32767}
    raster_image_math.do_avg_image(**args)

test_avg_firms()