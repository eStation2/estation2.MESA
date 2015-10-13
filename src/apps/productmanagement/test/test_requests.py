# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Jur van 't Klooster
#    date:     27.10.2015
#

from __future__ import absolute_import

import unittest
import os

from apps.productmanagement import requests

# from config import es_constants
# from lib.python import functions
# from database import connectdb
# from database import querydb
from lib.python import es_logging as log
logger = log.my_logger(__name__)


class TestRequests(unittest.TestCase):

    def test_requests(self):
        productcode = 'vgt-ndvi'
        version = 'spot-v2'
        mapsetcode = 'SPOTV-Africa-1km'
        subproductcode = 'ndv'
        request = requests.create_request(productcode, version, mapsetcode=None, subproductcode=None)
        print request
