# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Jur van 't Klooster
#    date:     27.10.2015
#

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
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

        print (request_json)

    def test_requests_new_dekad(self):
        getparams = {
            'level': 'dataset',
            'productcode': 'vgt-ndvi',
            'version': 'sv2-pv2.2',
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

        print (request_json)

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

        print (request_json)

    # Type 1: only product/version defined
    def test_requests_1(self):

        test_json_dump = req_dir+'dump_my_json_1.req'
        mapsetcode = None
        subproductcode = None

        # The case below FAILS !! -> to be double-checked
        # productcode = 'lsasaf-lst'
        # version = 'undefined'

        # productcode = 'vgt-ndvi'
        # version = 'sv2-pv2.2'
        # mapsetcode = 'SPOTV-Africa-1km'
        # # mapsetcode = 'SPOTV-IGAD-1km'
        # # subproductcode = 'ndvi-linearx2'

        productcode = 'olci-wrr'
        version = 'V02.0'
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

        print (test_json_dump)

    # Type 2: product/version/mapset defined
    def test_requests_2(self):

        req_dir=es_constants.es2globals['requests_dir']
        test_json_dump=req_dir+'/dump_my_json_2.req'
        productcode = 'vgt-ndvi'
        # version = 'sv2-pv2.1'
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

        print (request_json)

    # Type 3: product/version/mapset/subproduct defined
    def test_requests_3(self):

        req_dir=es_constants.es2globals['requests_dir']
        test_json_dump=req_dir+'/dump_my_json_2.req'
        productcode = 'vgt-ndvi'
        version = 'spot-v1'
        mapsetcode = 'SPOTV-Africa-1km'
        subproductcode = 'ndv'
        request = requests.create_request(productcode, version, mapsetcode=mapsetcode, subproductcode=subproductcode)
        request_json = json.dumps(request,
                               ensure_ascii=False,
                               sort_keys=True,
                               indent=4,
                               separators=(', ', ': '))

        with open(test_json_dump,'w+') as f:
            f.write(request_json)
        f.close()

        print (request_json)


class TestCreateArchives(unittest.TestCase):

    # Create a .bsx archive by using the method: create_archive_vars()
    # It does not go through the 'request' creation.

    def test_create_archive_vars(self):

        #   Creates and archive for a single product/sproduct/mapset/period
        productcode='vgt-ndvi'
        subproductcode = 'ndv'
        version = 'sv2-pv2.2'
        mapsetcode = 'SPOTV-SADC-1km'
        from_date='2018-12-11'
        to_date='2018-12-21'
        output_dir='/eStation2/archives/bsx/'

        bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode, from_date, to_date,
                                               output_dir=output_dir)

        logger.info('Archive created as {0}'.format(bsx_archive))

        return

    # Create a .bsx archives for NDVI 2.2
    def test_achive_creation_ndvi_2_2(self):

        #   General definitions
        productcode='vgt-ndvi'
        version = 'sv2-pv2.2'
        output_dir='/data/bsx_archives/'

        #   ================================================================
        #   10d linearx2 LTA
        #   ================================================================

        subproductcodes = ('10davg-linearx2','10dmin-linearx2','10dmax-linearx2','10dmed-linearx2')
        regions=('IGAD','ECOWAS','SADC','CEMAC')
        from_date = None
        to_date = None
        for subproductcode in subproductcodes:
            for region in regions:

                mapsetcode='SPOTV-{0}-1km'.format(region)
                output_subdir='/data/bsx_archives/{0}'.format(region)

                bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode,
                                                           from_date=from_date, to_date=to_date, time_suffix='36-dekads', output_dir=output_subdir)

                logger.info('Archive created as {0}'.format(bsx_archive))



    # Create a .bsx archives for MODIS-SST (for subsetting to IOC region)
    def test_achive_creation_modis_sst(self):

        #   General definitions
        productcode='modis-sst'
        version = 'v2013.1'
        output_dir='/data/bsx_archives/'

        #   ================================================================
        #
        #   ================================================================

        subproductcodes = ('monavg','monclim','monanom')
        from_date = '2010-01-01'
        to_date = '2017-07-01'
        for subproductcode in subproductcodes:

                mapsetcode='MODIS-IOC-4km'
                output_subdir='/data/bsx_archives/{0}'.format(mapsetcode)

                bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode,
                                                           from_date=from_date, to_date=to_date, time_suffix='2010-2017', output_dir=output_subdir)

                logger.info('Archive created as {0}'.format(bsx_archive))

    # Create a .bsx archives for MODIS-CHLA (for subsetting to IOC region)
    def test_achive_creation_modis_chla(self):

        #   General definitions
        productcode='modis-chla'
        version = 'v2013.1'
        output_dir='/data/bsx_archives/'

        #   ================================================================
        #
        #   ================================================================

        subproductcodes = ('monavg','monclim','monanom')
        from_date = '2010-01-01'
        to_date = '2017-07-01'
        for subproductcode in subproductcodes:

                mapsetcode='MODIS-IOC-4km'
                output_subdir='/data/bsx_archives/{0}'.format(mapsetcode)

                bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode,
                                                           from_date=from_date, to_date=to_date, time_suffix='2010-2017', output_dir=output_subdir)

                logger.info('Archive created as {0}'.format(bsx_archive))

    def test_achive_creation_ndvi_bdms(self):

        #   General definitions
        productcode='vgt-ndvi'
        version = 'sv2-pv2.2'
        output_dir='/data/bsx_archives/'

        #   ================================================================
        #   10d linearx2 LTA
        #   ================================================================

        subproductcodes = ['ndv']
        regions=['SADC']
        from_date = '2018-12-11'
        to_date = '2018-12-21'
        for subproductcode in subproductcodes:
            for region in regions:

                mapsetcode='SPOTV-{0}-1km'.format(region)
                output_subdir='/data/bsx_archives/{0}'.format(region)

                bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode,
                                                           from_date=from_date, to_date=to_date, time_suffix='36-dekads', output_dir=output_subdir)

                logger.info('Archive created as {0}'.format(bsx_archive))


