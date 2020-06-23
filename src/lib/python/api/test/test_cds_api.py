from unittest import TestCase
from lib.python.api import cds_api
from lib.python import es_logging as log

import os

logger = log.my_logger(__name__)


class TestCDSAPI(TestCase):

    def test_get_resources(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd=None
        https_params=None
        response = cds_api.get_resources_list(base_url, usr_pwd, https_params)
        return True

    def test_get_resource_details(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd=None
        https_params=None
        resourcename_uuid='satellite-sea-surface-temperature'
        response = cds_api.get_resource_details(base_url, resourcename_uuid,usr_pwd, https_params)
        return True

    def test_get_resource_details(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        resourcename_uuid='satellite-sea-surface-temperature'
        response = cds_api.get_resource_availablity(base_url, resourcename_uuid,usr_pwd, https_params)
        return response

    def test_get_resource_details(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        # resourcename_uuid='reanalysis-era5-land'
        # template= {'format': 'netcdf', 'variable': ['lake_mix_layer_temperature', 'skin_temperature'  ], 'year': [ '2018', '2019'],  'day': '01', 'time': '00:00', 'month': '01'}
        resourcename_uuid = 'reanalysis-era5-single-levels-monthly-means'
        template= {'format': 'netcdf', 'product_type': ['monthly_averaged_ensemble_members', 'monthly_averaged_ensemble_members_by_hour_of_day', 'monthly_averaged_reanalysis','monthly_averaged_reanalysis_by_hour_of_day'],'year': '2015','month': '01', 'variable': 'convective_precipitation','time': '00:00'}
        response = cds_api.post_request_resource(base_url, resourcename_uuid, usr_pwd, https_params, template)
        return response

    def test_get_tasks_list(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        response = cds_api.get_tasks_list(base_url,usr_pwd, https_params)
        return True

    def test_get_task_details(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        request_id='b8943fe2-6b86-4c8a-ad6c-a0bd8583e904'
        response = cds_api.get_task_details(base_url, request_id,usr_pwd, https_params)
        return True

    def test_get_file(self):
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        # request_id='dcf3a6ae-4bc5-4256-9ad0-02e1ec8fb8e3'
        download_location = 'http://136.156.133.36/cache-compute-0010/cache/data6/adaptor.mars.internal-1583247782.7579274-16775-20-79492323-19b3-413d-bd3c-cbd194333ed4.nc'
        target_path = '/data/ingest/test.nc'
        response = cds_api.get_file(download_location, usr_pwd, https_params, target_path)
        return True

    def test_delete_task(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        request_id='b8943fe2-6b86-4c8a-ad6c-a0bd8583e904'
        response = cds_api.delete_cds_task(base_url, request_id,usr_pwd, https_params)
        return True

    def test_get_termsConditions_list(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd=None
        https_params=None
        response = cds_api.get_termsConditions_list(base_url, usr_pwd, https_params)
        return True

    def test_get_user_termsConditions_list(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        https_params=None
        response = cds_api.get_user_termsConditions_list(base_url, usr_pwd, https_params)
        return True

    def test_accept_termsConditions_list(self):
        base_url='https://cds.climate.copernicus.eu/api/v2'
        usr_pwd='32952:f0154805-2620-4288-a412-18bc89b98c7d'
        terms_list = [{
            "terms_id": "cems-floods",
            "revision": 1,
            "title": "CEMS-FLOODS datasets licence",
            "display_url": "/api/v2/terms/static/cems-floodsv1.md",
            "download_url": "/api/v2/terms/static/cems-floods.pdf"
        }]
        https_params=None
        response = cds_api.accept_termsConditions_list(base_url, terms_list, usr_pwd, https_params)
        return True

