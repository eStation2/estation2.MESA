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
from database import querydb
from apps.acquisition import get_internet
#from apps.acquisition.test import test_get_interneT
from apps.acquisition import acquisition

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

                result = get_internet.loop_get_internet(test_one_source=internet_id, my_source=my_source)
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

                result = get_internet.loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(0, 0)


    def testRemote_CDS_SST_1DAY(self):
        internet_id = 'JRC:MARS:WSI:CROP'
        template= {"resourcename_uuid" : "reanalysis-era5-single-levels", "format": "netcdf", "product_type": "reanalysis",
        "variable": "sea_surface_temperature",
        "year": "2019","month": "01","day":"01","time": "12:00"}
        remote_url='https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/'
        from_date = '20200610'
        to_date = '20200620'
        frequency = 'e1hour'
        my_source = SourceEOS(internet_id=internet_id,
                              url=remote_url,
                              descriptive_name='CDS',
                              include_files_expression=template,
                              pull_frequency=3,
                              user_name='32952',
                              password='f0154805-2620-4288-a412-18bc89b98c7d',
                              start_date=from_date,
                              end_date=to_date,
                              frequency_id=frequency,
                              type='cds_api',
                              files_filter_expression='sst',
                              https_params='')

        #files_list = get_internet.build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
        result = get_internet.loop_get_internet(test_one_source=internet_id, my_source=my_source)

