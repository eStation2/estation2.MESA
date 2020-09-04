# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Jur van 't Klooster
#    date:     27.10.2015
#

from __future__ import absolute_import

import unittest
import json
import pprint
import datetime as dt

from apps.productmanagement import requests
from apps.productmanagement import products

from config import es_constants
from lib.python import es_logging as log
from apps.productmanagement import requests
from lib.python import functions

logger = log.my_logger(__name__)

req_dir=es_constants.es2globals['requests_dir']


class TestCreateRequests(unittest.TestCase):

    def test_requests_new_highfrequency(self):
        getparams = {
            'level': 'dataset',
            'productcode': 'lsasaf-lst',
            'version': 'undefined',
            'mapsetcode': 'MSG-satellite-3km',
            'subproductcode': 'lst',
            'dekad_frequency': '5',
            'daily_frequency': '3',
            'high_frequency': '3'
        }
        productcode = None
        version = None
        mapsetcode = None
        subproductcode = None

        productcode = getparams['productcode']
        version = getparams['version']
        if getparams['level'] == 'mapset':
            mapsetcode = getparams['mapsetcode']
        if getparams['level'] == 'dataset':
            mapsetcode = getparams['mapsetcode']
            subproductcode = getparams['subproductcode']

        request = requests.create_request(productcode,
                                          version,
                                          mapsetcode=mapsetcode,
                                          subproductcode=subproductcode,
                                          dekad_frequency=int(getparams['dekad_frequency']),
                                          daily_frequency=int(getparams['daily_frequency']),
                                          high_frequency=int(getparams['high_frequency']))
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))
        # Check the request for LST requests has the correct subproduct (see ES2-596)
        self.assertEqual(request['productmapsets'][0]['mapsetdatasets'][0]['subproductcode'],'lst')

    def test_requests_new_dekad(self):
        getparams = {
            'level': 'dataset',
            'productcode': 'vgt-ndvi',
            'version': 'sv2-pv2.1',
            'mapsetcode': 'SPOTV-Africa-1km',
            'subproductcode': 'ndv',
            'dekad_frequency': '5',
            'daily_frequency': '3',
            'high_frequency': '3'
        }
        productcode = None
        version = None
        mapsetcode = None
        subproductcode = None

        if getparams['level'] == 'product':
            productcode = getparams['productcode']
            version = getparams['version']
        elif getparams['level'] == 'mapset':
            productcode = getparams['productcode']
            version = getparams['version']
            mapsetcode = getparams['mapsetcode']
        elif getparams['level'] == 'dataset':
            productcode = getparams['productcode']
            version = getparams['version']
            mapsetcode = getparams['mapsetcode']
            subproductcode = getparams['subproductcode']

        request = requests.create_request(productcode,
                                          version,
                                          mapsetcode=mapsetcode,
                                          subproductcode=subproductcode,
                                          dekad_frequency=int(getparams['dekad_frequency']),
                                          daily_frequency=int(getparams['daily_frequency']),
                                          high_frequency=int(getparams['high_frequency']))
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        # Check the request for NDVI requests has the correct subproduct (see ES2-596)
        self.assertEqual(request['productmapsets'][0]['mapsetdatasets'][0]['subproductcode'],'ndv')

    def test_requests_new_daily(self):
        getparams = {
            'level': 'dataset',
            'productcode': 'arc2-rain',
            'version': '2.0',
            'mapsetcode': 'ARC2-Africa-11km',
            'subproductcode': '1day',
            'dekad_frequency': '5',
            'daily_frequency': '3',
            'high_frequency': '3'
        }
        productcode = None
        version = None
        mapsetcode = None
        subproductcode = None

        if getparams['level'] == 'product':
            productcode = getparams['productcode']
            version = getparams['version']
        elif getparams['level'] == 'mapset':
            productcode = getparams['productcode']
            version = getparams['version']
            mapsetcode = getparams['mapsetcode']
        elif getparams['level'] == 'dataset':
            productcode = getparams['productcode']
            version = getparams['version']
            mapsetcode = getparams['mapsetcode']
            subproductcode = getparams['subproductcode']

        request = requests.create_request(productcode,
                                          version,
                                          mapsetcode=mapsetcode,
                                          subproductcode=subproductcode,
                                          dekad_frequency=int(getparams['dekad_frequency']),
                                          daily_frequency=int(getparams['daily_frequency']),
                                          high_frequency=int(getparams['high_frequency']))
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        # Check the request for NDVI requests has the correct subproduct (see ES2-596)
        self.assertEqual(request['productmapsets'][0]['mapsetdatasets'][0]['subproductcode'],'1day')

suite_requests = unittest.TestLoader().loadTestsFromTestCase(TestCreateRequests)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_requests)
