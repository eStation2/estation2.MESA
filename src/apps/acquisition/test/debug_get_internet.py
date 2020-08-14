from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

from future import standard_library

standard_library.install_aliases()
from apps.acquisition.test.test_get_internet import *
from database import querydb

#   ---------------------------------------------------------------------------
#    OCEANOGRAPHY - Sentinel 3 OLCI WRR - JEODESK EOS file system
#   ---------------------------------------------------------------------------
def testLocal_EOS_JEODESK_OLCI(self):
    source_active = False
    internet_id = 'EOS:S3A:OLCI:WRR'
    start_date_fixed = 20200301
    end_date_fixed = 20200310
    start_date_dyn = -2
    end_date_dyn = -1
    file_to_check = '44c285d7-3809-4810-836e-510ee52f326a/S3A_OL_2_WRR____20200310T065044_20200310T073438_20200311T133228_2634_056_006______MAR_O_NT_002'

    internet_sources = querydb.get_active_internet_sources()
    for s in internet_sources:
        if s.internet_id == internet_id:
            internet_source = s
            source_active = True

    if source_active:
        my_source = Source(internet_id=internet_id,
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

        if True:
            result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
            self.assertEqual(result, 0)

#   ---------------------------------------------------------------------------
#    OCEANOGRAPHY - Sentinel 3 SLSTR WST - JEODESK EOS file system
#   ---------------------------------------------------------------------------
def testLocal_EOS_JEODESK_SLSTR(self):
    source_active = False
    internet_id = 'EOS:S3A:SLSTR:WST'
    start_date_fixed = 20200301
    end_date_fixed = 20200310
    start_date_dyn = -5
    end_date_dyn = -3
    file_to_check = '32e61b08-0bcb-4d0a-a06e-f3d499dfb5fc/S3A_SL_2_WST____20200310T073813_20200310T091913_20200311T185257_6059_056_006______MAR_O_NT_003'

    internet_sources = querydb.get_active_internet_sources()
    for s in internet_sources:
        if s.internet_id == internet_id:
            internet_source = s
            source_active = True

    if source_active:
        my_source = Source(internet_id=internet_id,
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
        if True:
            result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
            self.assertEqual(result, 0)