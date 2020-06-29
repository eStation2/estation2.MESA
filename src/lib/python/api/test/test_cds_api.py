from unittest import TestCase
from lib.python.api import cds_api
from lib.python import es_logging as log
from config import es_constants

import os

logger = log.my_logger(__name__)


class TestCDSAPI(TestCase):
    def setUp(self):
        root_test_dir = es_constants.es2globals['test_data_dir']
        self.test_ingest_dir = root_test_dir  # os.path.join(root_test_dir,'native')
        self.proc_dir_bck = es_constants.processing_dir
        es_constants.processing_dir = es_constants.es2globals['base_tmp_dir'] + os.path.sep
        self.ingest_out_dir = es_constants.processing_dir
        self.usr_pwd = '32952:f0154805-2620-4288-a412-18bc89b98c7d'
        self.base_url='https://cds.climate.copernicus.eu/api/v2'
        self.native_dir = 'native'

    def test_get_resources(self):
        https_params=None
        response = cds_api.get_resources_list(self.base_url, self.usr_pwd, https_params)
        return True

    def test_get_resource_details(self):
        https_params=None
        resourcename_uuid='reanalysis-era5-single-levels'
        response = cds_api.get_resource_details(self.base_url, resourcename_uuid, self.usr_pwd, https_params)
        return True

    def test_get_resource_availablity(self):
        https_params=None
        resourcename_uuid='reanalysis-era5-single-levels'
        response = cds_api.get_resource_availablity(self.base_url, resourcename_uuid, self.usr_pwd, https_params)
        return response

    def test_get_resource(self):
        https_params=None
        # resourcename_uuid='reanalysis-era5-land'
        # template= {'format': 'netcdf', 'variable': ['lake_mix_layer_temperature', 'skin_temperature'  ], 'year': [ '2018', '2019'],  'day': '01', 'time': '00:00', 'month': '01'}
        resourcename_uuid = 'reanalysis-era5-single-levels'
        template= {'format': 'netcdf', 'product_type': 'reanalysis',
        'variable': 'sea_surface_temperature',
        'year': '2019','month': '01','day':'01','time': '12:00'}
        response = cds_api.post_request_resource(self.base_url, resourcename_uuid, self.usr_pwd, https_params, template)
        return response

    def test_get_tasks_list(self):
        https_params=None
        response = cds_api.get_tasks_list(self.base_url, self.usr_pwd, https_params)
        return True

    def test_get_task_details(self):
        https_params=None
        request_id='c982dc60-e520-4982-8789-dd5d89e17b49'
        response = cds_api.get_task_details(self.base_url, request_id, self.usr_pwd, https_params)
        return True

    def test_get_file(self):
        # request_id='c982dc60-e520-4982-8789-dd5d89e17b49'
        download_location = 'http://136.156.132.105/cache-compute-0000/cache/data7/adaptor.mars.internal-1593013385.3229878-9139-14-bdb03ac5-0602-48fb-8e6b-f734c74a1ea0.nc'
        target_path = self.test_ingest_dir+'/sst.nc'
        response = cds_api.get_file(download_location, self.usr_pwd, target_path)
        return True

    def test_delete_task(self):
        https_params=None
        request_id='c982dc60-e520-4982-8789-dd5d89e17b49'
        response = cds_api.delete_cds_task(self.base_url, request_id, self.usr_pwd, https_params)
        return True

    def test_get_termsConditions_list(self):
        https_params=None
        response = cds_api.get_termsConditions_list(self.base_url, self.usr_pwd, https_params)
        return True

    def test_get_user_termsConditions_list(self):
        https_params=None
        response = cds_api.get_user_termsConditions_list(self.base_url, self.usr_pwd, https_params)
        return True

    def test_accept_termsConditions_list(self):
        terms_list = [{
            "terms_id": "cems-floods",
            "revision": 1,
            "title": "CEMS-FLOODS datasets licence",
            "display_url": "/api/v2/terms/static/cems-floodsv1.md",
            "download_url": "/api/v2/terms/static/cems-floods.pdf"
        }]
        https_params=None
        response = cds_api.accept_termsConditions_list(self.base_url, terms_list, self.usr_pwd, https_params)
        return True

