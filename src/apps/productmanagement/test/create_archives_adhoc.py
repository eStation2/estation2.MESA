# -*- coding: utf-8 -*-

#
#    purpose: Test products functions
#    author:  Jur van 't Klooster
#    date:     27.10.2015
#

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function

from future import standard_library
standard_library.install_aliases()
import unittest
import json
# import pprint
# import datetime as dt
#
# from apps.productmanagement import requests
# from apps.productmanagement import products

from config import es_constants
from lib.python import es_logging as log
from apps.productmanagement import requests
# from lib.python import functions

logger = log.my_logger(__name__)

req_dir=es_constants.es2globals['requests_dir']


class TestCreateArchives(unittest.TestCase):

    # Create a .bsx archive by defining 'manually' the missing files ('ad-hoc')
    # It does not go through the 'request' creation.

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

        output_dir='/data/bsx_archives/'
        regions=['SADC']
        time_suffix='Dec-2018'
        from_date = '2018-12-11'
        to_date = '2018-12-21'

        #   ================================================================
        #   Missing 2 NDVI dekads - December 2018
        #   ================================================================

        productcode='vgt-ndvi'
        version = 'sv2-pv2.2'
        subproductcodes = ['ndv']
        for subproductcode in subproductcodes:
            for region in regions:

                mapsetcode='SPOTV-{0}-1km'.format(region)
                output_subdir=output_dir+'/{0}'.format(region)

                bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode,
                                                           from_date=from_date, to_date=to_date, time_suffix=time_suffix, output_dir=output_subdir)

                logger.info('Archive created as {0}'.format(bsx_archive))

        #   ================================================================
        #   Missing 2 VCI dekads - December 2018
        #   ================================================================

        # productcode='vgt-ndvi'
        # version = 'sv2-pv2.2'
        # subproductcodes = ['ndv']
        # for subproductcode in subproductcodes:
        #     for region in regions:
        #
        #         mapsetcode='SPOTV-{0}-1km'.format(region)
        #         output_subdir=output_dir+'/{0}'.format(region)
        #
        #         bsx_archive = requests.create_archive_vars(productcode, version, mapsetcode, subproductcode,
        #                                                    from_date=from_date, to_date=to_date, time_suffix=time_suffix, output_dir=output_subdir)
        #
        #         logger.info('Archive created as {0}'.format(bsx_archive))
        #

