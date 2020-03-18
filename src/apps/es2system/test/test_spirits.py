from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = 'analyst'


from database import querydb
from lib.python import functions
from lib.python import es_logging as log
from apps.es2system import convert_2_spirits as conv
logger = log.my_logger(__name__)
from unittest import TestCase

class TestSpirits(TestCase):
    def test_spirits_modify_header(self):

        # Should get here the role of my machine ...
        header_file = '/data/processing/exchange/spirits/SPOTV-Africa-1km/vgt-ndvi/it10/vt20180101i.hdr'

        metadata_spirits= {'description': 'NDVI v2.2'}
                           # 'flags': '{-32768=missing}', \
                           # 'data_ignore_value':'-32768', \
                           # 'days': 10, \
                           # 'sensor_type':'SPOT VGT-PROBA V', \
                           # 'comment':'Smoothed NDVI v2.1, JRC eStation2.0',
                           # 'date':''}
        conv.append_to_header_file(header_file, metadata_spirits)

    def test_convert_1_file(self):

        naming_spirits = { 'sensor_filename_prefix':'v', \
                           'frequency_filename_prefix':'t', \
                           'pa_filename_prefix':'k'}

        metadata_spirits= {'values': '{NDVI, -, 0, 1000, 0, 1000, 0, 0.001}',
                           'flags': '{-32768=missing}', \
                           'data_ignore_value':'-32768', \
                           'days': 10, \
                           'sensor_type':'SPOT VGT-PROBA V', \
                           'comment':'Smoothed NDVI v2.1, JRC eStation2.0',
                           'date':''}

        input_file='/data/processing/vgt-ndvi/sv2-pv2.1/SPOTV-Africa-1km/tif/ndv/20110101_vgt-ndvi_ndv_SPOTV-Africa-1km_sv2-pv2.1.tif'
        output_dir = '/data/temp/spirits'
        str_date = '20110101'
        metadata_spirits['date']=str_date
        conv.convert_geotiff_file(input_file, output_dir, str_date, naming_spirits, metadata_spirits)

    def test_driver(self):
        output_dir = '/data/processing/exchange/spirits/'
        conv.convert_driver(output_dir)
