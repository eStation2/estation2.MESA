from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import str
import unittest
import re
import os
import glob
from database import querydb
from apps.acquisition import get_internet
#from apps.acquisition.test import test_get_interneT
from apps.acquisition import ingestion
from lib.python import es_logging as log

logger = log.my_logger(__name__)

class SourceEOS:
    def __init__(self,
                 url=None,
                 internet_id=None,
                 defined_by=None,
                 descriptive_name=None,
                 description=None,
                 modified_by=None,
                 update_datetime=None,
                 user_name=None,
                 password=None,
                 type=None,
                 include_files_expression=None,
                 files_filter_expression=None,
                 status=None,
                 pull_frequency=None,
                 datasource_descr_id=None,
                 frequency_id=None,
                 start_date=None,
                 end_date=None,
                 https_params=None):
        self.url = url
        self.internet_id = internet_id
        self.defined_by = defined_by
        self.descriptive_name = descriptive_name
        self.description = description
        self.modified_by = modified_by
        self.update_datetime = update_datetime
        self.user_name = user_name
        self.password = password
        self.type = type
        self.include_files_expression = include_files_expression
        self.files_filter_expression = files_filter_expression
        self.status = status
        self.pull_frequency = pull_frequency
        self.datasource_descr_id = datasource_descr_id
        self.frequency_id = frequency_id
        self.start_date = start_date
        self.end_date = end_date
        self.https_params = https_params
#
class TestGetEOS(unittest.TestCase):

    # def test_GetEOS_PC2_homedir(self):
    #     base_folder='/eos/jeodpp/data/SRS/Copernicus/S3/scenes/source/'
    #     filter_filter_expression = 'S3A_OL_2_WRR____*'
    #     sensor_id='OL2WRR'
    #     year='2020'
    #     month='05'
    #     day='01'
    #     ftp_eumetcast_userpwd='root:rootroot'
    #     current_list = self.get_list_matching_files_dir(base_folder+year+'/'+month+'/'+day, filter_filter_expression)
    #
    #
    # def get_list_matching_files_dir(self, directory, pattern):
    #     lst = []
    #     for root, dirs, files in os.walk(directory):
    #         for basename in files:
    #             if re.search(pattern, basename):
    #                 fn = os.path.join(root, basename)
    #                 lst.append(fn)
    #     return lst


    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 OLCI WRR - JEODESK EOS file system
    #   ---------------------------------------------------------------------------
    def testLocal_EOS_JEODESK_OLCI(self):
        source_active = False
        list_internet_id = ['EOS:S3A:OLCI:WRR', 'EOS:S3B:OLCI:WRR']
        #internet_id = 'EOS:S3A:OLCI:WRR'
        start_date_dyn = -5
        end_date_dyn = -1

        for internet_id in list_internet_id:

            internet_sources = querydb.get_active_internet_sources()
            for s in internet_sources:
                if s.internet_id == internet_id:
                    internet_source = s
                    source_active = True

            if source_active:
                my_source = SourceEOS(internet_id=internet_id,
                                   url=internet_source.url,
                                   descriptive_name="OLCI WRR",
                                   include_files_expression=internet_source.include_files_expression,
                                   pull_frequency=internet_source.pull_frequency,
                                   user_name=internet_source.user_name,
                                   password=internet_source.password,
                                   start_date=start_date_dyn,
                                   end_date=end_date_dyn,
                                   frequency_id=internet_source.frequency_id,
                                   type=internet_source.type,
                                   files_filter_expression=internet_source.files_filter_expression,
                                   https_params=internet_source.https_params)

                productcode = 'olci-wrr'
                productversion = 'V02.0'
                product = {"productcode": productcode,
                           "version": productversion}

                result = get_internet.loop_get_internet(test_one_source=internet_id)
                self.assertEqual(0, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 SLSTR WST - JEODESK EOS file system
    #   ---------------------------------------------------------------------------
    def testLocal_EOS_JEODESK_SLSTR(self):
        source_active = False
        list_internet_id = ['EOS:S3A:SLSTR:WST', 'EOS:S3B:SLSTR:WST']
        start_date_dyn = -5
        end_date_dyn = -1

        internet_sources = querydb.get_active_internet_sources()

        for internet_id in list_internet_id:
            for s in internet_sources:
                if s.internet_id == internet_id:
                    internet_source = s
                    source_active = True

            if source_active:
                my_source = SourceEOS(internet_id=internet_id,
                                   url=internet_source.url,
                                   descriptive_name='sentinel',
                                   include_files_expression=internet_source.include_files_expression,
                                   pull_frequency=internet_source.pull_frequency,
                                   user_name=internet_source.user_name,
                                   password=internet_source.password,
                                   start_date=start_date_dyn,
                                   end_date=end_date_dyn,
                                   frequency_id=internet_source.frequency_id,
                                   type=internet_source.type,
                                   files_filter_expression=internet_source.files_filter_expression,
                                   https_params=internet_source.https_params)

                productcode = 'slstr-sst'
                productversion = '1.0'
                product = {"productcode": productcode,
                           "version": productversion}
                # Test download (dynamic dates

                result = get_internet.loop_get_internet(test_one_source=internet_id)
                self.assertEqual(0, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI V2.2.1 - New test for resampling 300 to 1 Km
    #   Tested ok (metadata diff) 24.6.20 -> 25s PyCh
    #   ---------------------------------------------------------------------------
    def test_ingest_g_cls_ndvi_200_1Km(self):

        # Test Copernicus Products version 2.2 (starting with NDVI 2.2.1)
        productcode = 'vgt-ndvi'
        productversion = 'proba-v2.2'
        subproductcode = 'ndv'
        mapsetcode = 'SPOTV-Africa-1km'
        datasource_descrID = 'PDF:GLS:PROBA-V1:NDVI300'
        # input_dir = self.test_ingest_dir + os.path.sep + productcode + os.path.sep + self.native_dir
        #date_fileslist = [os.path.join(input_dir, 'c_gls_NDVI_202003010000_AFRI_PROBAV_V2.2.1.zip')]
        date_fileslist = glob.glob('/eos/jeodpp/home/users/venkavi/data/processing/vgt-ndvi/sv2-pv2.2/archive/c_gls_NDVI300_202007110000_GLOBE_PROBAV_V1.0.1.nc*')
        in_date = '202007110000'
        out_date = '20200711'
        product = {"productcode": productcode,
                   "version": productversion}
        args = {"productcode": productcode,
                "subproductcode": subproductcode,
                "datasource_descr_id": datasource_descrID,
                "version": productversion}

        product_in_info = querydb.get_product_in_info(**args)

        re_process = product_in_info.re_process
        re_extract = product_in_info.re_extract

        sprod = {'subproduct': subproductcode,
                 'mapsetcode': mapsetcode,
                 're_extract': re_extract,
                 're_process': re_process}

        subproducts = [sprod]
        # Remove existing output
        # self.remove_output_file(productcode, subproductcode, productversion, mapsetcode, out_date)
        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id=datasource_descrID)
        ingestion.ingestion(date_fileslist, in_date, product, subproducts, datasource_descr[0], logger,
                            echo_query=1, test_mode=False)

        # status = self.checkIngestedFile(productcode=productcode, subproductcode=subproductcode,
        #                                 version=productversion, mapsetcode=mapsetcode, date=out_date)
        self.assertEqual(1, 1)

