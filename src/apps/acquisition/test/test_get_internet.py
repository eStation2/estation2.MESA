
from config import es_constants
from apps.acquisition.get_internet import *
from apps.acquisition.get_eumetcast import *
# from apps.tools import coda_eum_api

import unittest

logger = log.my_logger(__name__)

#
#   Extracted from loo_get_internet to get a single source
#


class Source:
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

class TestGetInternet(unittest.TestCase):

    pattern = True
    download = False
    direct_download = False
    target_dir = '/data/tmp'

    # def setUp(self):
    #     # Suppress logging
    #     log.disable(logging.CRITICAL)
    #
    # def tearDown(self):
    #     # RE-ACTIVATE logging
    #     logging.disable(logging.NONSET)

    #   ---------------------------------------------------------------------------
    #   Vegetation - WSI CROP
    #   ---------------------------------------------------------------------------
    def test_RemoteHttp_WSI_CROP(self):
        source_active = False
        internet_id = 'JRC:MARS:WSI:CROP'
        start_date_fixed = 20200201
        end_date_fixed = 20200321
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'wsi_hp_crop_20200201.img'
        include_files_expression = "wsi_hp_crop_%Y%m%d.img"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MARS HP for crop',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)
            # Direct test !
            if self.direct_download:
                filename = 'wsi_hp_crop_20200201.hdr'
                remote_url = internet_source.url + '/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)
            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=True)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates)
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - WSI PASTURE
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_WSI_PASTURE(self):
        source_active = False
        internet_id = 'JRC:MARS:WSI:PASTURE'
        start_date_fixed = 20200201
        end_date_fixed = 20200321
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'wsi_hp_pasture_20200201.img'
        include_files_expression = "wsi_hp_pasture_%Y%m%d.img"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MARS HP for pasture',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'wsi_hp_pasture_20200201.hdr'
                remote_url = internet_source.url + '/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=True)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - DMP RTO
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_DMP_RTO(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V2.0:DMP_RT0'
        start_date_fixed = 20200201
        end_date_fixed = 20200321
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2020/3/10/DMP-RT0_202003100000_GLOBE_PROBAV_V2.0.1/c_gls_DMP-RT0_202003100000_GLOBE_PROBAV_V2.0.1.nc'
        include_files_expression = "/%Y/%-m/%d/DMP-RT0_%Y%m%d0000_GLOBE_PROBAV_V2.0.1/c_gls_DMP-RT0_%Y%m%d0000_GLOBE_PROBAV_V2.0.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - DMP 2.0 Prelimary',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'c_gls_DMP-RT0_202003100000_GLOBE_PROBAV_V2.0.1.nc'
                remote_url = internet_source.url + '/2020/3/10/DMP-RT0_202003100000_GLOBE_PROBAV_V2.0.1/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - DMP RT6
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_DMP(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V2.0:DMP'
        start_date_fixed = 20191010
        end_date_fixed = 20191210
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2019/11/10/DMP-RT6_201911100000_GLOBE_PROBAV_V2.0.1/c_gls_DMP-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
        include_files_expression = "/%Y/%-m/%d/DMP-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1/c_gls_DMP-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - DMP 2.0',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'c_gls_DMP-RT6_201801100000_GLOBE_PROBAV_V2.0.1.nc'
                remote_url = internet_source.url + '/2018/1/10/DMP-RT6_201801100000_GLOBE_PROBAV_V2.0.1/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)
            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FAPAR RT6
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_FAPAR(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V2.0:FAPAR'
        start_date_fixed = 20191010
        end_date_fixed = 20191210
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2019/11/10/FAPAR-RT6_201911100000_GLOBE_PROBAV_V2.0.1/c_gls_FAPAR-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
        include_files_expression = "/%Y/%-m/%d/FAPAR-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1/c_gls_FAPAR-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - FAPAR 2.0 (offline retrieval)',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'c_gls_FAPAR-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
                remote_url = internet_source.url + '/2019/11/10/FAPAR-RT6_201911100000_GLOBE_PROBAV_V2.0.1/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - FCOVER RT6
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_FCOVER(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V2.0:FCOVER'
        start_date_fixed = 20191010
        end_date_fixed = 20191210
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2019/11/10/FCOVER-RT6_201911100000_GLOBE_PROBAV_V2.0.1/c_gls_FCOVER-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
        include_files_expression = "/%Y/%-m/%d/FCOVER-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1/c_gls_FCOVER-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - FCOVER 2.0 (offline retrieval)',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'c_gls_FCOVER-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
                remote_url = internet_source.url + '/2019/11/10/FCOVER-RT6_201911100000_GLOBE_PROBAV_V2.0.1/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - LAI RT6
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_LAI(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V2.0:LAI'
        start_date_fixed = 20191010
        end_date_fixed = 20191210
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2019/11/10/LAI-RT6_201911100000_GLOBE_PROBAV_V2.0.1/c_gls_LAI-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
        include_files_expression = "/%Y/%-m/%d/LAI-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1/c_gls_LAI-RT6_%Y%m%d0000_GLOBE_PROBAV_V2.0.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - LAI 2.0 (offline retrieval)',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'c_gls_LAI-RT6_201911100000_GLOBE_PROBAV_V2.0.1.nc'
                remote_url = internet_source.url + '/2019/11/10/LAI-RT6_201911100000_GLOBE_PROBAV_V2.0.1/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_NDVI(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V2.2:NDVI'
        start_date_fixed = 20191010
        end_date_fixed = 20191210
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2019/11/01/NDVI_201911010000_GLOBE_PROBAV_V2.2.1/c_gls_NDVI_201911010000_GLOBE_PROBAV_V2.2.1.nc'
        include_files_expression = "/%Y/%-m/%d/NDVI_%Y%m%d0000_GLOBE_PROBAV_V2.2.1/c_gls_NDVI_%Y%m%d0000_GLOBE_PROBAV_V2.2.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - NDVI 2.0 (offline retrieval)',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'c_gls_NDVI_202003010000_GLOBE_PROBAV_V2.2.1.nc'
                remote_url = internet_source.url + '/2020/03/01/NDVI_202003010000_GLOBE_PROBAV_V2.2.1/' + filename
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Vegetation - NDVI 300m
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_NDVI300(self):
        source_active = False
        internet_id = 'PDF:VITO:PROBA-V1:NDVI300'
        start_date_fixed = 20200201
        end_date_fixed = 20200201
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2020/02/01/PV_S10_TOC_NDVI-20200201_333M_V101/PROBAV_S10_TOC_X19Y05_20200201_333M_NDVI_V101_NDVI.tif'
        include_files_expression = "/%Y/%m/%d/PV_S10_TOC_NDVI-%Y%m%d_333M_V101/PROBAV_S10_TOC_@@@@_%Y%m%d_333M_NDVI_V101_NDVI.tif"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - NDVI 300m',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'PROBAV_S10_TOC_X19Y05_20200201_333M_NDVI_V101_NDVI.tif'
                remote_url = internet_source.url + file_to_check
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password,
                                           https_params='Referer: ' + str(internet_source.url) + os.path.dirname(
                                               filename) + '?mode=tif')
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl_vito(str(internet_source.url), include_files_expression,
                                                       start_date_fixed,
                                                       end_date_fixed,
                                                       str(internet_source.frequency_id),
                                                       )
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Rainfall - ARC2
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_ARC2(self):
        source_active = False
        internet_id = 'CPC:NOAA:RAIN:ARC2'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'africa_arc.20200120.tif.zip'
        include_files_expression = "africa_arc.%Y%m%d.tif.zip"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='ARC-2 rain from CPC-NASA',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'africa_arc.20200120.tif.zip'
                remote_url = internet_source.url + file_to_check
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Rainfall - CHIRPS PREL
    #   ---------------------------------------------------------------------------
    def testRemoteFtp_CHIRPS_PREL(self):
        source_active = False
        internet_id = 'UCSB:CHIRPS:PREL:DEKAD'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'chirps-v2.0.2020.02.3.tif'
        include_files_expression = "chirps-v2.0.20[12].*.tif$"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='CHIRPS preliminary precipitation, dekad type, globally, V2.0',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'chirps-v2.0.2020.02.3.tif'
                remote_url = internet_source.url + file_to_check
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = get_list_matching_files(str(internet_source.url),
                                           internet_source.user_name + ':' + internet_source.password,
                                           include_files_expression, internet_source.type)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   Rainfall -  CHIRP (id: UCSB:CHIRP:DEKAD) NOT USED IN ESTATION
    #   ---------------------------------------------------------------------------
    # def testRemoteFtp_CHIRP(self):
    #     # Retrieve a list of CHIRP
    #     remote_url='ftp://chg-ftpout.geog.ucsb.edu/pub/org/chg/products/CHIRP/pentads/'
    #     usr_pwd='anonymous:anonymous'
    #     full_regex   ='CHIRP.2014.12.[1-3].tif'
    #     file_to_check='CHIRP.2014.12.1.tif'
    #     internet_type = 'ftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #    Rainfall - CHIRPS (id:  UCSB:CHIRPS:DEKAD:2.0)
    #   ---------------------------------------------------------------------------
    def testRemoteFtp_CHIRPS_2_0(self):
        source_active = False
        internet_id = 'UCSB:CHIRPS:DEKAD:2.0'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'chirps-v2.0.2020.01.1.tif.gz'
        include_files_expression = "chirps-v2.0.20[12].*.tif.gz"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='CHIRPS final precipitation, dekad type, globally, V2.0',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'chirps-v2.0.2020.01.1.tif.gz'
                remote_url = internet_source.url + file_to_check
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = get_list_matching_files(str(internet_source.url),
                                           internet_source.user_name + ':' + internet_source.password,
                                           include_files_expression, internet_source.type)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Rainfall - Fewsnet 2
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_FEWSNET_2(self):
        source_active = False
        internet_id = 'USGS:EARLWRN:FEWSNET'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'a20031rb.zip'
        include_files_expression = "a%y%m%{dkm}rb.zip"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='FEWSNET Rainfall Estimate for Africa',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'a20031rb.zip'
                remote_url = str(internet_source.url + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename)
                self.assertEqual(status, 0)
            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Rainfall - JRC MARS SPI 3MON
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_MARS_SPI_3MON(self):
        source_active = False
        internet_id = 'JRC:MARS:SPI:3MON'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'spi3_20200201.img'
        include_files_expression = "spi3_%Y%m%d.img,spi3_%Y%m%d.hdr"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='JRC MARS SPI 3-month time scale',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'spi3_20200201.img'
                remote_url = str(internet_source.url + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename)
                self.assertEqual(status, 0)
            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=True)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Rainfall - JRC MARS SPI 1MON
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_MARS_SPI_1MON(self):
        source_active = False
        internet_id = 'JRC:MARS:SPI:1MON'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'spi1_20200201.img'
        include_files_expression = "spi1_%Y%m%d.img,spi1_%Y%m%d.hdr"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='JRC MARS SPI 1-month time scale',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'spi1_20200201.img'
                remote_url = str(internet_source.url + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=True)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Rainfall - TAMSAT 3
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_TAMSAT_3(self):
        source_active = False
        internet_id = 'READINGS:TAMSAT:3.0:10D:NC'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'TAMSAT3/2020/02/rfe2020_02-dk1.v3.nc'
        include_files_expression = "TAMSAT3/%Y/%m/rfe%Y_%m-dk%{dkm}.v3.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='TAMSAT Version 3.0 data from Readings website',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'rfe2020_02-dk1.v3.nc'
                remote_url = str(internet_source.url + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename)
                self.assertEqual(status, 0)
            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    FIRE - MODIS FIRMS 6
    #   ---------------------------------------------------------------------------
    def test_RemoteHttps_MODIS_FIRMS_6(self):
        source_active = False
        internet_id = 'MODAPS:EOSDIS:FIRMS:NASA:HTTP'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'MODIS_C6_Global_MCD14DL_NRT_2020060.txt'
        include_files_expression = "MODIS_C6_Global_MCD14DL_NRT_%Y%j.txt"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODAPS NRT3 server at EOSDIS/NASA',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test !
            if self.direct_download:
                filename = 'MODIS_C6_Global_MCD14DL_NRT_2020060.txt'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password,
                                           https_params=internet_source.https_params)
                self.assertEqual(status, 0)
            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    FIRE - PROBA BA 300
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_BA300(self):
        source_active = False
        internet_id = 'PDF:GLS:PROBA-V1.1:BA300'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2020/2/10/BA300_202002100000_GLOBE_PROBAV_V1.1.1/c_gls_BA300_202002100000_GLOBE_PROBAV_V1.1.1.nc'
        include_files_expression = "/%Y/%-m/%d/BA300_%Y%m%d0000_GLOBE_PROBAV_V1.1.1/c_gls_BA300_%Y%m%d0000_GLOBE_PROBAV_V1.1.1.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - BA 1.1.1 300m',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'c_gls_BA300_202002100000_GLOBE_PROBAV_V1.1.1.nc'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password)
                self.assertEqual(status, 0)

            # Test pattern (with fixed date)
            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS CHLA
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_MODIS_CHL(self):
        source_active = False
        internet_id = 'GSFC:CGI:MODIS:CHLA:1D'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'A2020060.L3m_DAY_CHL_chlor_a_4km.nc'
        include_files_expression = "A%Y%j.L3m_DAY_CHL_chlor_a_4km.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODIS 4km Chla Daily',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'A2020060.L3m_DAY_CHL_chlor_a_4km.nc'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                                            userpwd=internet_source.user_name + ':' + internet_source.password,
                                            https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS KD490
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_MODIS_KD490(self):
        source_active = False
        internet_id = 'GSFC:CGI:MODIS:KD490:1D'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'A2020060.L3m_DAY_KD490_Kd_490_4km.nc'
        include_files_expression = "A%Y%j.L3m_DAY_KD490_Kd_490_4km.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODIS 4km Kd490 Daily',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'A2020060.L3m_DAY_KD490_Kd_490_4km.nc'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                                            userpwd=internet_source.user_name + ':' + internet_source.password,
                                            https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS PAR
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_MODIS_PAR(self):
        source_active = False
        internet_id = 'GSFC:CGI:MODIS:PAR:1D'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'A2020060.L3m_DAY_PAR_par_4km.nc'
        include_files_expression = "A%Y%j.L3m_DAY_PAR_par_4km.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODIS 4km Par Daily',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'A2020060.L3m_DAY_PAR_par_4km.nc'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                                            userpwd=internet_source.user_name + ':' + internet_source.password,
                                            https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MODIS SST
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_MODIS_SST(self):
        source_active = False
        internet_id = 'GSFC:CGI:MODIS:SST:1D:NEW'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'AQUA_MODIS.20200301.L3m.DAY.SST.sst.4km.NRT.nc'
        include_files_expression = "AQUA_MODIS.%Y%m%d.L3m.DAY.SST.sst.4km.NRT.nc"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODIS 4km SST Daily',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'AQUA_MODIS.20200301.L3m.DAY.SST.sst.4km.NRT.nc'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                                            userpwd=internet_source.user_name + ':' + internet_source.password,
                                            https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl(str(internet_source.url), include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - PML MODIS SST
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_PML_MODIS_SST(self):
        source_active = False
        internet_id = 'PML:SST:1D'
        start_date_fixed = 20200301
        end_date_fixed = 20200315
        start_date_dyn = -45
        end_date_dyn = -30
        # ES2-596 -> change date to dynamic
        file_to_check = 'PML_CapeVerde_MODIS_sst_3daycomp_20200901_20200903.nc.bz2'
        include_files_expression = "PML_.*_MODIS_sst_3daycomp.*.nc.bz2"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODIS/PML SST - Composite Ocean Products - Multimission - AMESD Regions',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'PML_CapeVerde_MODIS_sst_3daycomp_20200310_20200312.nc.bz2'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password,
                                           https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = get_list_matching_files(str(internet_source.url),
                                           internet_source.user_name + ':' + internet_source.password,
                                           include_files_expression, internet_source.type, end_date=end_date_fixed)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - PML MODIS CHL
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_PML_MODIS_CHL(self):
        source_active = False
        internet_id = 'PML:CHL:1D'
        start_date_fixed = 20200301
        end_date_fixed = 20200315
        start_date_dyn = -45
        end_date_dyn = -30
        # ES2-596 -> Change date to dynamic
        file_to_check = 'PML_CapeVerde_MODIS_oc_3daycomp_20200901_20200903.nc.bz2'
        include_files_expression = "PML_.*_MODIS_oc_3daycomp.*.nc.bz2"

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MODIS/PML CHL - Composite Ocean Products - Multimission - AMESD Regions',
                               include_files_expression=include_files_expression,
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'PML_CapeVerde_MODIS_oc_3daycomp_20200308_20200310.nc.bz2'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
                                           userpwd=internet_source.user_name + ':' + internet_source.password,
                                           https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = get_list_matching_files(str(internet_source.url),
                                           internet_source.user_name + ':' + internet_source.password,
                                           include_files_expression, internet_source.type)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - MOTU - This test is check the MOTU functionality not for the product
    #   ---------------------------------------------------------------------------
    # def TestMOTU(self):
    #     source_active = False
    #     internet_id='MOTU:PHY:TDS'
    #     start_date = 20200101
    #     end_date = 20200310
    #     file_to_check = 'PML_CapeVerde_MODIS_oc_3daycomp_20200308_20200310.nc.bz2'
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #             source_active = True
    #
    #     if source_active:
    #         my_source =     {'internet_id': internet_id,
    #                          'url': internet_source.url,
    #                          'include_files_expression':internet_source.include_files_expression,
    #                          'pull_frequency': internet_source.pull_frequency,
    #                          'user_name':internet_source.user_name,
    #                          'password':internet_source.password,
    #                          'start_date':-2,
    #                          'end_date': 8,
    #                          'frequency_id': internet_source.frequency_id,
    #                          'type':internet_source.type,
    #                          'files_filter_expression':internet_source.files_filter_expression,
    #                          'https_params': '',
    #
    #         }
    #
    #         # Direct test ! True: #
    #         if self.direct_download:
    #             filename = 'PML_CapeVerde_MODIS_oc_3daycomp_20200308_20200310.nc.bz2'
    #             remote_url = str(internet_source.url + '/' + file_to_check)
    #             status = get_file_from_url(remote_url, self.target_dir, target_file=filename,
    #                                        userpwd=internet_source.user_name + ':' + internet_source.password,
    #                                        https_params=internet_source.https_params)
    #             self.assertEqual(status, 0)
    #         # Unitest test !
    #         if False: #self.Unitest_pattern:
    #             list = get_list_matching_files(str(internet_source.url),
    #                                            internet_source.user_name + ':' + internet_source.password,
    #                                            internet_source.include_files_expression, internet_source.type)
    #             self.assertTrue(file_to_check in list)
    #         else:
    #             result = get_one_source(my_source)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 OLCI WRR
    #   ---------------------------------------------------------------------------
    def testLocal_CODA_EUM_OLCI(self):
        source_active = False
        internet_id = 'CODA:EUM:S3A:OLCI:WRR'
        start_date_fixed = 20200301
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
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

            # Direct test ! True: #
            if self.direct_download:
                filename = os.path.split(file_to_check)[1]
                remote_url = str(internet_source.url + '/' + file_to_check)
                download_link = 'https://coda.eumetsat.int/odata/v1/Products(\'{0}\')/$value'.format(
                    os.path.split(file_to_check)[0])
                status = get_file_from_url(str(download_link), target_dir=es_constants.ingest_dir,
                                           target_file=os.path.basename(filename) + '.zip',
                                           userpwd=str(internet_source.user_name + ':' + internet_source.password),
                                           https_params=str(internet_source.https_params))
                # status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                #                            userpwd=internet_source.user_name + ':' + internet_source.password, https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_eum_http(str(internet_source.url),
                                                      internet_source.include_files_expression, start_date_fixed,
                                                      end_date_fixed, internet_source.frequency_id,
                                                      internet_source.user_name, internet_source.password)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    OCEANOGRAPHY - Sentinel 3 SLSTR WST
    #   ---------------------------------------------------------------------------
    def testLocal_CODA_EUM_SLSTR(self):
        source_active = False
        internet_id = 'CODA:EUM:S3A:SLSTR:WST'
        start_date_fixed = 20200301
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
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

            # Direct test ! True: #
            if self.direct_download:
                filename = os.path.split(file_to_check)[1]
                remote_url = str(internet_source.url + '/' + file_to_check)
                download_link = 'https://coda.eumetsat.int/odata/v1/Products(\'{0}\')/$value'.format(
                    os.path.split(file_to_check)[0])
                status = get_file_from_url(str(download_link), target_dir=es_constants.ingest_dir,
                                           target_file=os.path.basename(filename) + '.zip',
                                           userpwd=str(internet_source.user_name + ':' + internet_source.password),
                                           https_params=str(internet_source.https_params))
                # status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                #                            userpwd=internet_source.user_name + ':' + internet_source.password, https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_eum_http(str(internet_source.url),
                                                      internet_source.include_files_expression, start_date_fixed,
                                                      end_date_fixed, internet_source.frequency_id,
                                                      internet_source.user_name, internet_source.password)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)



    def testLocal_MOTU(self):
        source_active = False
        internet_id='MOTU:BIO:TDS'
        start_date_fixed = 20200301
        end_date_fixed = 20200310
        start_date_dyn = -5
        end_date_dyn = 5
        # file_to_check = '32e61b08-0bcb-4d0a-a06e-f3d499dfb5fc/S3A_SL_2_WST____20200310T073813_20200310T091913_20200311T185257_6059_056_006______MAR_O_NT_003'

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='MOTU',
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

        # list = build_list_matching_files_eum_http(str(internet_source.url),
        #                                           internet_source.include_files_expression, start_date_fixed,
        #                                           end_date_fixed, internet_source.frequency_id,
        #                                           internet_source.user_name, internet_source.password)
        # if self.pattern:
        #     self.assertTrue(file_to_check in list)

        # Test download (dynamic dates
        if self.download:
            result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
            self.assertEqual(result, 0)


    #   ---------------------------------------------------------------------------
    #    Miscellaneous - ASCAT SWI
    #   ---------------------------------------------------------------------------
    def testLocal_ASCAT_SWI(self):
        source_active = False
        internet_id = 'PDF:GLS:METOP:ASCAT-V3.1:SWI'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = '/2020/02/10/SWI_202002101200_GLOBE_ASCAT_V3.1.1/c_gls_SWI_202002101200_GLOBE_ASCAT_V3.1.1.nc'

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='VITO PDF server - SWI 3.0',
                               include_files_expression="/%Y/%m/%d/SWI_%Y%m%d1200_GLOBE_ASCAT_V3.1.1/c_gls_SWI_%Y%m%d1200_GLOBE_ASCAT_V3.1.1.nc",
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)
            # Direct test ! True: #
            if self.direct_download:
                filename = 'c_gls_SWI_202002101200_GLOBE_ASCAT_V3.1.1.nc'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(str(remote_url), target_dir=self.target_dir,
                                           target_file=filename,
                                           userpwd=str(internet_source.user_name + ':' + internet_source.password),
                                           https_params=str(internet_source.https_params))
                # status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                #                            userpwd=internet_source.user_name + ':' + internet_source.password, https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl(str(internet_source.url), internet_source.include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Miscellaneous - CPC SM
    #   ---------------------------------------------------------------------------
    def testRemoteHttp_CPC_SM(self):
        source_active = False
        internet_id = 'CPC:NCEP:NOAA:SM'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'w.202002.mon'

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='CPC Soil Moisture from NCEP',
                               include_files_expression="w.%Y%m.mon",
                               pull_frequency=internet_source.pull_frequency,
                               user_name=internet_source.user_name,
                               password=internet_source.password,
                               start_date=start_date_dyn,
                               end_date=end_date_dyn,
                               frequency_id=internet_source.frequency_id,
                               type=internet_source.type,
                               files_filter_expression=internet_source.files_filter_expression,
                               https_params=internet_source.https_params)

            # Direct test ! True: #
            if self.direct_download:
                filename = 'w.202002.mon'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(str(remote_url), target_dir=self.target_dir,
                                           target_file=filename,
                                           userpwd=str(internet_source.user_name + ':' + internet_source.password),
                                           https_params=str(internet_source.https_params))
                # status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                #                            userpwd=internet_source.user_name + ':' + internet_source.password, https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl(str(internet_source.url), internet_source.include_files_expression,
                                                  start_date_fixed,
                                                  end_date_fixed,
                                                  str(internet_source.frequency_id),
                                                  multi_template=False)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Miscellaneous - JEODPP SENTINEL 2
    #   ---------------------------------------------------------------------------
    def TestRemoteJEODPP_S2LIC(self):
        source_active = False
        internet_id = 'JRC:JEODPP:S2:L1C'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'S2B_MSIL1C_20200218T073949_N0209_R092_T36LZQ_20200218T095106:B12'

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='JEODPP',
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

            # Direct test ! True: #
            if self.direct_download:
                filename = 'w.202002.mon'
                remote_url = str(internet_source.url + '/' + file_to_check)
                status = get_file_from_url(str(remote_url), target_dir=self.target_dir,
                                           target_file=filename,
                                           userpwd=str(internet_source.user_name + ':' + internet_source.password),
                                           https_params=str(internet_source.https_params))
                # status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
                #                            userpwd=internet_source.user_name + ':' + internet_source.password, https_params=internet_source.https_params)
                self.assertEqual(status, 0)

            list = build_list_matching_files_jeodpp(str(internet_source.url), internet_source.include_files_expression,
                                                    start_date_fixed,
                                                    end_date_fixed,
                                                    str(internet_source.frequency_id),
                                                    str('venkavi:NEVZ9n3XDHSXkDzo'))
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #    Miscellaneous - SENTINEL SAT API
    #   ---------------------------------------------------------------------------
    # def TestLocal_SENTINELSAT(self):
    #     source_active = False
    #     internet_id='SENTINEL2:S2MSI1C:XYZ'
    #     start_date_fixed = 20200101
    #     end_date_fixed = 20200310
    #     start_date_dyn = -45
    #     end_date_dyn = -30
    #     # file_to_check = 'S2B_MSIL1C_20200218T073949_N0209_R092_T36LZQ_20200218T095106:B12'
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #             source_active = True
    #
    #     if source_active:
    #         my_source = Source(internet_id=internet_id,
    #                            url=internet_source.url,
    #                            descriptive_name='JEODPP',
    #                            include_files_expression=internet_source.include_files_expression,
    #                            pull_frequency=internet_source.pull_frequency,
    #                            user_name=internet_source.user_name,
    #                            password=internet_source.password,
    #                            start_date=start_date_dyn,
    #                            end_date=end_date_dyn,
    #                            frequency_id=internet_source.frequency_id,
    #                            type=internet_source.type,
    #                            files_filter_expression=internet_source.files_filter_expression,
    #                            https_params=internet_source.https_params)
    #
    #         # # Direct test ! True: #
    #         # if self.direct_download:
    #         #     filename = 'w.202002.mon'
    #         #     remote_url = str(internet_source.url + '/' + file_to_check)
    #         #     status = get_file_from_url(str(remote_url), target_dir=self.target_dir,
    #         #                                target_file=filename,
    #         #                                userpwd=str(internet_source.user_name + ':' + internet_source.password),
    #         #                                https_params=str(internet_source.https_params))
    #         #     # status = wget_file_from_url(remote_url, self.target_dir, target_file=filename,
    #         #     #                            userpwd=internet_source.user_name + ':' + internet_source.password, https_params=internet_source.https_params)
    #         #     self.assertEqual(status, 0)
    #         #
    #         # list = build_list_matching_files_jeodpp(str(internet_source.url), internet_source.include_files_expression,
    #         #                                         start_date_fixed,
    #         #                                         end_date_fixed,
    #         #                                         str(internet_source.frequency_id),
    #         #                                         str('venkavi:NEVZ9n3XDHSXkDzo'))
    #         # if self.pattern:
    #         #     self.assertTrue(file_to_check in list)
    #
    #         # Test download (dynamic dates
    #         if self.download:
    #             result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
    #             self.assertEqual(result, 0)

    #   ---------------------------------------------------------------------------
    #   INLAND WATER - WATERLEVEL
    #   ---------------------------------------------------------------------------
    def testRemoteHttps_WATERLEVEL(self):
        source_active = False
        internet_id = 'THEIA:HYDRO:LEGOS:WATERLEVEL'
        start_date_fixed = 20200101
        end_date_fixed = 20200310
        start_date_dyn = -45
        end_date_dyn = -30
        file_to_check = 'authdownload?products=R_con_con_s3a_0427_00&sdate=2020-02-01&edate=2020-02-11&format=csv&user=mesa.cwg@gmail.com&pwd=eStation2019/hydroprd_R_con_con_s3a_0427_00_from_2020-02-01_to_2020-02-11.csv'

        internet_sources = querydb.get_active_internet_sources()
        for s in internet_sources:
            if s.internet_id == internet_id:
                internet_source = s
                source_active = True

        if source_active:
            my_source = Source(internet_id=internet_id,
                               url=internet_source.url,
                               descriptive_name='TAMSAT Version 3.0 data from Readings website',
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

            # Direct test ! True: #
            if self.direct_download:
                file_to_check = 'authdownload?products=R_con_con_s3a_0427_00&sdate=2020-02-01&edate=2020-02-29&format=csv&user=mesa.cwg@gmail.com&pwd=eStation2019/hydroprd_R_con_con_s3a_0427_00_from_2020-02-01_to_2020-02-29.csv'
                filename = os.path.basename(os.path.split(file_to_check)[1])
                remote_url = str(internet_source.url + os.path.sep + os.path.split(file_to_check)[0])
                status = get_file_from_url(str(remote_url), target_dir=self.target_dir,
                                           target_file=filename,
                                           userpwd=str(internet_source.user_name + ':' + internet_source.password),
                                           https_params=str(internet_source.https_params))
                self.assertEqual(status, 0)

            list = build_list_matching_files_tmpl_theia(str(internet_source.url),
                                                        internet_source.include_files_expression,
                                                        start_date_fixed,
                                                        end_date_fixed,
                                                        str(internet_source.frequency_id),
                                                        internet_source.user_name,
                                                        internet_source.password)
            if self.pattern:
                self.assertTrue(file_to_check in list)

            # Test download (dynamic dates
            if self.download:
                result = loop_get_internet(test_one_source=internet_id, my_source=my_source)
                self.assertEqual(result, 0)

    # def TestGetInfo(self):
    #
    #     eum_id = 'EO:EUM:DAT:MSG:LST-SEVIRI'
    #     info = get_eumetcast_info(eum_id)
    #
    # def TestLocalDir(self):
    #     local_dir='/data/eumetcast_S3/'
    #     regex='S3A*'
    #     list = get_list_matching_files_dir_local(local_dir, regex)
    #     self.assertTrue(1)

    #   ---------------------------------------------------------------------------
    #   Get contents of a remote MODIS BA  (id: UMD:MCD45A1:TIF:51)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_MCD45A1_TIF(self):
    #     remote_url='ftp://ba1.geog.umd.edu/Collection51/TIFF/'
    #     usr_pwd='user:burnt_data'
    #     full_regex   ='Win11/2011/MCD45monthly.*.burndate.tif.gz'
    #     file_to_check='Win11/2011/MCD45monthly.A2011001.Win11.051.burndate.tif.gz'
    #     internet_type = 'ftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Get contents of a remote MODIS BA  (id: UMD:MCD45A1:HDF:51)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_MCD45A1_HDF(self):
    #     remote_url='ftp://ba1.geog.umd.edu/Collection51/HDF/'
    #     usr_pwd='user:burnt_data'
    #     #full_regex   ='20../.../MCD45A1.A.*.hdf'
    #     full_regex   ='2011/.../MCD45A1.A.*.hdf'
    #     file_to_check='2011/001/MCD45A1.A2011001.h05v10.051.2013067232210.hdf'
    #     internet_type = 'ftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test remote ftp NASA_FIRMS (id: USGS:FIRMS)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_FIRMS_NASA(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='ftp://nrt1.modaps.eosdis.nasa.gov/FIRMS/Global/'
    #     usr_pwd='user:burnt_data'
    #     full_regex   ='Global_MCD14DL_201.*.txt'
    #     file_to_check='Global_MCD14DL_2016100.txt'
    #     internet_type = 'ftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex, internet_type)
    #
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test remote ftp NOAA GSOD (id: NOAA:GSOD)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_NOAA_GSOD(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='ftp://ftp.ncdc.noaa.gov/pub/data/gsod/'
    #     usr_pwd='anonymous:'
    #     full_regex   ='2011/997...-99999-2011.op.gz'
    #     file_to_check='2011/997286-99999-2011.op.gz'
    #     internet_type = 'ftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #     print (list)
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test JRC sftp : does not work !!!
    #   ---------------------------------------------------------------------------

    # def TestRemoteFtp_JRC_S3A_WRR(self):
    #
    #     # Retrieve the S3A OLCI WRR products from JRC sftp site
    #     remote_url='sftp://srv-ies-ftp.jrc.it/'
    #     usr_pwd='narmauser:JRCkOq7478'
    #     full_regex   ='narma/eumetcast/S3A/S3A_OL_2_WRR_*'
    #     file_to_check='narma/eumetcast/S3A/S3A_OL_2_WRR____20180819T124041_20180819T132454_20180819T152131_2653_034_366______MAR_O_NR_002.SEN3.tar'
    #     internet_type = 'sftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #     print (list)
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test remote ftp JRC -> obsolete
    #   This was a work-around for collection 5, but moving to collection 6 the
    #   direct download from MODAPS:EOSDIS:NASA:FIRMS works !
    #
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_JRC(self):
    #
    #     # Retrieve a list files from JRC ftp -> ftp-type contents (not through proxy)
    #     remote_url='ftp://h05-ftp.jrc.it/'
    #     usr_pwd='narmauser:2016mesa!'
    #     full_regex   ='/eStation_2.0/Documents/DesignDocs/'
    #     file_to_check='SRD_eStation_MESA_1.5.pdf'
    #     internet_type = 'ftp'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #
    #     self.assertTrue(file_to_check in list)
    #
    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. ARC2)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_ARC2(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='ftp://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/arc2/geotiff/'
    #     usr_pwd='anonymous:@'
    #     full_regex   ='africa_arc.2015.....tif.zip'
    #     file_to_check='africa_arc.20150121.tif.zip'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex)
    #
    #     self.assertTrue(file_to_check in list)
    #
    # #   ---------------------------------------------------------------------------
    # #   Test iteration on remote ftp (e.g. CAMS_OPI)
    # #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_CAMS_OPI(self):
    #
    #     # Retrieve a list of CQMS-OPI .. check only one present
    #     remote_url='ftp://ftp.cpc.ncep.noaa.gov/precip/data-req/cams_opi_v0208/'
    #     usr_pwd='anonymous:@'
    #     full_regex   ='africa_arc.2015.....tif.zip'
    #     file_to_check='africa_arc.20150121.tif.zip'
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex)
    #
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Test iteration on remote ftp (e.g. VITO GL-GIO products): Obsolete ?
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_FTP_VITO(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='ftp://catftp.vgt.vito.be/'
    #     usr_pwd='estationJRC:eStation14'
    #     full_regex   ='/^[A-Za-z0-9].*/^g2_BIOPAR_.*zip$'
    #     file_to_check=''
    #
    #     list = get_list_matching_files(remote_url, usr_pwd, full_regex)
    #
    #     self.assertTrue(file_to_check in list)

    #   ---------------------------------------------------------------------------
    #   Get list of files from FEWSNET HTTP (id: USGS:EARLWRN:FEWSNET)
    #   ---------------------------------------------------------------------------

    # # Test 2.0.3-9
    # def TestRemoteHttp_TAMSAT(self):
    #
    #     remote_url='https://tamsat.org.uk/public_data/'
    #     from_date = '20170701'
    #     to_date = '20170711'
    #     template=''
    #
    #     frequency = 'e1dekad'
    #
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #
    #     #file_to_check='2015/a15121rb.zip'
    #     #self.assertTrue(file_to_check in files_list)
    #
    #     status = get_file_from_url(remote_url+files_list[-1],  self.target_dir, target_file=None, userpwd='')

    # Original test
    # def TestRemoteHttp_FEWSNET(self):
    #
    #     remote_url='http://earlywarning.usgs.gov/ftp2/raster/rf/a/'
    #     from_date = '20151101'
    #     to_date = None
    #     template='%Y/a%y%m%{dkm}rb.zip'
    #     frequency = 'e1dekad'
    #
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #
    #     file_to_check='2015/a15121rb.zip'
    #     self.assertTrue(file_to_check in files_list)

    # # Test new version (2.0.3-9)
    # def TestRemoteHttp_FEWSNET_1(self):
    #
    #     remote_url=''   # Not used
    #     from_date = '20151101'
    #     template='%Y/a%y%m%{dkm}rb.zip'
    #     frequency = 'e1dekad'
    #
    #     # Check until current dekad (see output to terminal)
    #     to_date = ''
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print ("Current file: %s " % files_list[-1])
    #
    #     # Check until current dekad (see output to terminal)
    #     to_date = -10
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print ("Latest file: %s " % files_list[-1])
    #
    #     # Check from 6 months ago to now (should always be 18 files)
    #     from_date = -182
    #     to_date = ''
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     self.assertEqual(len(files_list),18)

    #   ---------------------------------------------------------------------------
    #   Test download of files from GSFC oceandata http site (id:GSFC:OCEAN:MODIS:SST:1D)
    #   ---------------------------------------------------------------------------

    # Original test
    # def TestRemoteHttp_MODIS_SST_1DAY(self):
    #
    #     remote_url='https://oceandata.sci.gsfc.nasa.gov/cgi/getfile/'
    #     from_date = '20161230'
    #     to_date = '20161231'
    #     template='A%Y%j.L3m_DAY_SST_sst_4km.nc'
    #     usr_pwd='anonymous:anonymous'
    #     frequency = 'e1day'
    #
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list)
    #     file_to_check='A2015211.L3m_DAY_SST_sst_4km.nc'
    #     self.assertTrue(file_to_check in files_list)

    # Test new version (2.0.3-9)

    # def TestRemoteHttp_MODIS_SST_1DAY_1(self):
    #
    #     remote_url='http://oceandata.sci.gsfc.nasa.gov/MODISA/Mapped/Daily/4km/SST/'
    #     remote_url=''   # Not used
    #     template='A%Y%j.L3m_DAY_SST_sst_4km.nc'
    #     frequency = 'e1day'
    #
    #     # Check until current day (check output to terminal)
    #     from_date = '20150707'
    #     to_date = ''
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list[-1])
    #
    #     # Check until yesterday (check output to terminal)
    #     from_date = '20150707'
    #     to_date = -1
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list[-1])
    #
    #     # Check last 30 days (check list length = 31)
    #     from_date = -30
    #     to_date = ''
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     self.assertEqual(len(files_list),31)

    #   ---------------------------------------------------------------------------
    #   Test download of Kd daily data from GSFC oceandata http site (id:GSFC:OCEAN:MODIS:KD:1D)
    #   ---------------------------------------------------------------------------
    # Original test
    # def TestRemoteHttp_MODIS_KD_1DAY(self):
    #
    #     remote_url='http://oceandata.sci.gsfc.nasa.gov/MODISA/Mapped/Daily/4km/Kd/'
    #     from_date = '20140101'
    #     to_date = '20141231'
    #     template='%Y/A%Y%j.L3m_DAY_KD490_Kd_490_4km.bz2'       # introduce non-standard placeholder
    #     usr_pwd='anonymous:anonymous'
    #     frequency = 'e1dekad'
    #
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list)
    #     file_to_check='2014/A2014001.L3m_DAY_KD490_Kd_490_4km.bz2'
    #     self.assertTrue(file_to_check in files_list)

    #   ---------------------------------------------------------------------------
    #   Test download of MOD09 files from USGS http site (id:MOD09GA_Africa)
    #   ---------------------------------------------------------------------------

    # Original test
    # def TestRemoteHttp_MOD09_GQ_005(self):
    #
    #     remote_url='http://e4ftl01.cr.usgs.gov/MOLT/MOD09GQ.005/2000.02.24/'
    #     remote_url='http://earlywarning.usgs.gov/ftp2/raster/rf/a/2014/'
    #     usr_pwd='anonymous:anonymous'
    #     c=pycurl.Curl()
    #     import io
    #     import io
    #     buffer = io.StringIO()
    #
    #     c.setopt(c.URL, remote_url)
    #     c.setopt(c.WRITEFUNCTION, buffer.write)
    #     c.perform()
    #     print (c.getinfo(pycurl.HTTP_CODE))
    #     html = buffer.getvalue()
    #
    #     file_to_check='2015/001/A2015001.L3m_DAY_SST_4.bz2'
    #     #results = re.search(r'(type="hidden" name="([0-9a-f]{32})")', html).group(2)
    #
    #     #self.assertTrue(file_to_check in results)

    #   ---------------------------------------------------------------------------
    #   Test download of WBD-JRC-GEE
    #   ---------------------------------------------------------------------------
    # Original test -> to be verified
    # def TestRemoteHttp_WBD_JRC(self):
    #
    #     remote_url='https://drive.google.com/drive/folders/0B92vEFOyFC5BcHJ1TkxWWnhjMHM/'
    #     from_date = datetime.date(2015,1,1)
    #     to_date = datetime.date(2015,12,31)
    #     template='%Y_%m/JRC_EXPORT*tif'
    #     usr_pwd='clerici.marco:marcle13'
    #     frequency = 'e1month'
    #     target_dir = '/data/ingest/temp/'
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     files_list = [remote_url+'2015_01/JRC_EXPORT_20160225110837299-0000000000-0000065536']
    #     get_file_from_url(files_list[0], target_dir, target_file=None, userpwd='', https_params='')
    #     print (files_list)

    #   ---------------------------------------------------------------------------
    #   Test remote http SPIRITS
    #   ---------------------------------------------------------------------------
    # Original test
    # def TestRemoteHttp_SPIRITS(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url='http://spirits.jrc.ec.europa.eu/files/ecmwf/ope/africa/rain/'
    #
    #     from_date = '20150101'
    #     to_date = '20151231'
    #     template='ope_africa_rain_%Y%m%d.zip'       # introduce non-standard placeholder
    #     usr_pwd='anonymous:anonymous'
    #     frequency = 'e1dekad'
    #
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list)
    #     file_to_check='ope_africa_rain_20150221.zip'
    #     self.assertTrue(file_to_check in files_list)

    # Test new version (2.0.3-9)
    # def TestRemoteHttp_SPIRITS_1(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     remote_url=''   # Not used
    #     template='ope_africa_rain_%Y%m%{dkm2}.zip'       # introduce non-standard placeholder
    #     frequency = 'e1dekad'
    #
    #     # Check until current day (check output to terminal)
    #     from_date = '20150701'
    #     to_date = ''
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list[-1])
    #
    #     # Check until 10 days ago (check output to terminal)
    #     to_date = -10
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     print (files_list[-1])
    #
    #     # Check last 90 days (check list length = 9)
    #     from_date = -90
    #     to_date = ''
    #     files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     self.assertEqual(len(files_list),9)
    #
    #
    # # Download LSASAF Orders
    # def TestRemoteFtp_Orders(self):
    #
    #     # Manually define relevant fields of internet source
    #     internet_source = {'internet_id': 'LSASAF_Orders',
    #                        'url': 'ftp://landsaf.ipma.pt/LSASAF-Dissemination/clerima/',
    #                        'include_files_expression': 'order_.*',
    #                        'pull_frequency': 1,
    #                        'user_name':'',
    #                        'password':'',
    #                        'start_date':None,
    #                        'end_date':None,
    #                        'type':'ftp'
    #                        }
    #
    #     result = get_one_source(internet_source)
    #
    # # Download LSASAF Orders
    #
    #
    #
    # # Download MODIS-FIRMS from h05-ftp.jrc.it
    # def TestRemoteFtp_JRC_FIRMS(self):
    #
    #     # Manually define relevant fields of internet source
    #     internet_source = {'internet_id': 'JRC:FTP:MCD14DL',
    #                        'url': 'ftp://h05-ftp.jrc.it/data/MCD14DL/',
    #                        'include_files_expression': 'Global_MCD14DL.*txt',
    #                        'pull_frequency': 1,
    #                        'user_name':'narmauser',
    #                        'password':'2016mesa!',
    #                        'start_date':None,
    #                        'end_date':None,
    #                        'type':'force_ftp'
    #                        }
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(internet_source)

    # def TestRemoteFtp_FEWSNET(self):
    #
    #     internet_id='USGS:EARLWRN:FEWSNET'
    #
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20170701,
    #                      'end_date':20170711,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type}
    #
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)

    # def TestRemoteHttp_ECMWF_evtp(self):
    #
    #     internet_id='ECMWF:MARS:EVPT:OPE'
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20161101,
    #                      'end_date':None,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type}
    #
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)

    #
    #
    # def Test_RemoteFtp_MODIS_FIRMS_6(self):
    #
    #     internet_id='MODAPS:EOSDIS:FIRMS:NASA'
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':  '20171201',
    #                      'end_date':None,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type}
    #
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)
    #
    #
    #
    #
    #
    #
    # def TestRemoteHttps_NDVI100(self):
    #
    #     internet_id='PDF:VITO:PROBA-V1:NDVI100'
    #
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20190601,
    #                      'end_date': 20190601,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type,
    #                      'https_params': internet_source.https_params}
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)
    #
    #
    #
    # def TestRemoteHttps_WSI(self):
    #
    #     internet_id='ECMWF:MARS:RAIN:WSI'
    #
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20190501,
    #                      'end_date': -20,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type,
    #                      'https_params': internet_source.https_params}
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)
    #
    #
    # def TestLocal_S3A_WST(self):
    #
    #     internet_id='JRC:S3A:WST'
    #
    #     # Direct test !
    #     if False:
    #         self.assertEqual(status, 0)
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20180610,
    #                      'end_date': 20180820,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type}
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)
    # def TestLocal_MOTU(self):
    #
    #     internet_id='CMEMS:MOTU:WAV:L4:SWH'
    #
    #     # Direct test !
    #     if False:
    #         self.assertEqual(status, 0)
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20200125,
    #                      'end_date': -1,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type,
    #                      'files_filter_expression':internet_source.files_filter_expression,
    #
    #     }
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)
    #



    #   ---------------------------------------------------------------------------
    #   Get contents of a remote MODIS BA  (id: UMD:MCD45A1:TIF:51)
    #   ---------------------------------------------------------------------------
    # def TestRemoteFtp_SMOS_NC(self):
    #
    #     remote_url = 'ftp://smos-diss.eo.esa.int/SMOS/L2OS/MIR_OSUDP2_nc/'
    #     from_date = '20190501' #datetime.date(2015,1,1)
    #     to_date = '20190515' #datetime.date(2015,12,31)
    #     template='/%Y/%m/%d/'
    #     file_exp = 'SM_OPER_MIR_OSUDP2_.*.nc'
    #     # usr_pwd='eStation2:eStation2019!'
    #     frequency = 'e1day'
    #     # target_dir = '/data/ingest/temp/'
    #     # files_list = build_list_matching_files_tmpl(remote_url, template, from_date, to_date, frequency)
    #     # # files_list = [remote_url+'2015_01/JRC_EXPORT_20160225110837299-0000000000-0000065536']
    #     # # get_file_from_url(files_list[0], target_dir, target_file=None, userpwd='', https_params='')
    #     # print files_list
    #
    #     usr_pwd='eStation2:eStation2019!'
    #     full_regex   ='SM_OPER_MIR_OSUDP2_.*.nc'
    #     file_to_check='/%Y/%m/SM_OPER_MIR_OSUDP2_.*.nc'
    #     internet_type = 'http'
    #
    #     #list = get_list_matching_files(remote_url, usr_pwd, full_regex,internet_type)
    #     list =  build_list_matching_files_ftp_tmpl(remote_url, template, from_date, to_date, frequency, usr_pwd, file_exp)
    #     self.assertTrue(file_to_check in list)
    #
    #
    # def TestFTP_TEMP_SMOS_NC(self):
    #
    #     internet_id='ESAEO:SMOS:L2OS:OSUDP2:SSS'
    #
    #     # Direct test !
    #     if False:
    #         self.assertEqual(status, 0)
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':20190805,
    #                      'end_date': 20190805,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type,
    #                      'files_filter_expression':internet_source.files_filter_expression,
    #                      'https_params': '',
    #
    #     }
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)

    # def TestRemoteHttp_ARC2(self):
    #
    #     # Retrieve a list of MODIS burndate file .. check only one present
    #     # remote_url='https://ftp.cpc.ncep.noaa.gov/fews/fewsdata/africa/arc2/geotiff/'
    #     internet_id='CPC:NOAA:RAIN:ARC2'
    #
    #     # Direct test !
    #     if False:
    #         self.assertEqual(status, 0)
    #
    #     internet_sources = querydb.get_active_internet_sources()
    #     for s in internet_sources:
    #         if s.internet_id == internet_id:
    #             internet_source = s
    #
    #     # Copy for modifs
    #     my_source =     {'internet_id': internet_id,
    #                      'url': internet_source.url,
    #                      'include_files_expression':internet_source.include_files_expression,
    #                      'pull_frequency': internet_source.pull_frequency,
    #                      'user_name':internet_source.user_name,
    #                      'password':internet_source.password,
    #                      'start_date':-15,
    #                      'end_date': -1,
    #                      'frequency_id': internet_source.frequency_id,
    #                      'type':internet_source.type,
    #                      'files_filter_expression':internet_source.files_filter_expression,
    #                      'https_params': '',
    #     }
    #
    #     # Check last 90 days (check list length = 9)
    #     result = get_one_source(my_source)

# suite_get_internet = unittest.TestLoader().loadTestsFromTestCase(TestGetInternet)
# if __name__ == '__main__':
#     unittest.TextTestRunner(verbosity=2).run(suite_get_internet)