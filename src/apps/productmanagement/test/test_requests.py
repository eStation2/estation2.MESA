# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Jur van 't Klooster
#    date:     27.10.2015
#

from __future__ import absolute_import

import unittest
import os
import json

from apps.productmanagement import requests

from config import es_constants
# from lib.python import functions
# from database import connectdb
# from database import querydb
from lib.python import es_logging as log
logger = log.my_logger(__name__)

req_dir=es_constants.es2globals['requests_dir']

class TestRequests(unittest.TestCase):


    def test_requests_1(self):

        test_json_dump=req_dir+'dump_my_json_1.req'
        mapsetcode = None
        subproductcode = None
        productcode = 'vgt-ndvi'
        # version = 'sv2-pv2.1'
        version = 'spot-v1'
        # mapsetcode = 'SPOTV-Africa-1km'
        # subproductcode = 'ndv'
        request = requests.create_request(productcode, version, mapsetcode=mapsetcode, subproductcode=subproductcode)
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        with open(test_json_dump,'w+') as f:
            f.write(request_json)
        f.close()

        print test_json_dump

    # def test_create_archive_1(self):
    #
    #     test_json_dump=req_dir+'dump_my_json_1.req'
    #
    #     with open(test_json_dump,'r') as f:
    #         request_json = f.read(test_json_dump)
    #     f.close()
    #
    #     print test_json_dump
    #



    def test_requests_2(self):

        req_dir=es_constants.es2globals['requests_dir']
        test_json_dump=req_dir+'/dump_my_json_2.req'
        productcode = 'vgt-ndvi'
        version = 'sv2-pv2.1'
        version = 'spot-v2'
        mapsetcode = 'SPOTV-Africa-1km'
        subproductcode = None
        request = requests.create_request(productcode, version, mapsetcode=mapsetcode, subproductcode=subproductcode)
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        with open(test_json_dump,'w+') as f:
            f.write(request_json)
        f.close()

        print request_json

    def test_requests_3(self):

        req_dir=es_constants.es2globals['requests_dir']
        test_json_dump=req_dir+'/dump_my_json_2.req'
        productcode = 'lsasaf-lst'
        version = 'lst'
        version = 'undefined'
        mapsetcode = None
        subproductcode = None
        request = requests.create_request(productcode, version, mapsetcode=mapsetcode, subproductcode=subproductcode)
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        with open(test_json_dump,'w+') as f:
            f.write(request_json)
        f.close()

        print request_json

