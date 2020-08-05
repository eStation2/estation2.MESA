from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from unittest import TestCase
from apps.tools.convert_to_ecoagris import *
from lib.python import es_logging as log

import os

logger = log.my_logger(__name__)


class TestEcoagris(TestCase):

    def test_NdviBenin(self):

        productinfo = {
            "productcode": 'vgt-ndvi',
            "version": 'sv2-pv2.2',
            "subproductcode": 'ndv',
            "mapsetcode": 'SPOTV-Africa-1km'
        }

        startdate = '2017-01-01'
        enddate = '2018-09-01'

        aggregateinfo = {'aggregation_type': 'mean',
                         'aggregation_min': None,
                         'aggregation_max': None}

        vectorlayer = '/eStation2/layers/BEN_adm/BEN_adm1.shp'
        regionidattr = 'HASC_1'
        regionlevel = 'admin1'

        # For debugging
        if os.path.isfile(vectorlayer):
            ecoagric_record = convert_to_ecoargis(productinfo, startdate, enddate, aggregateinfo, vectorlayer, regionidattr, regionlevel)
        else:
            logger.error('Vector layer file does not exist: %s' % vectorlayer)


        print (" \n  Results for Product  : {}".format(ecoagric_record["productcode"]))
        print ("  Results for Version  : {}".format(ecoagric_record["version"]))
        print ("  Results for Sprod    : {}".format(ecoagric_record["subproductcode"]))
        print ("  Results for date     : {}".format(ecoagric_record["product_date"]))
        print ("  Results for RegionLvl: {}".format(ecoagric_record["regionlevel"]))
        print ("  Results for RegionID : {}".format(ecoagric_record["regionid"]))
        print ("  Value is             : {}".format(ecoagric_record["tsvalue"]))

        self.assertAlmostEqual(ecoagric_record["tsvalue"],0.65758685521452676)

    def test_RFEBenin(self):

        productinfo = {
            "productcode": 'tamsat-rfe',
            "version": '2.0',
            "subproductcode": '10d',
            "mapsetcode": 'TAMSAT-Africa-4km'
        }

        startdate = '2017-01-01'
        enddate = '2018-05-01'

        aggregateinfo = {'aggregation_type': 'mean',
                         'aggregation_min': None,
                         'aggregation_max': None}

        vectorlayer = '/eStation2/layers/BEN_adm/BEN_adm1.shp'
        regionidattr = 'HASC_1'

        regionlevel = 'admin1'

        if os.path.isfile(vectorlayer):
            ecoagric_record = convert_to_ecoargis(productinfo, startdate, enddate, aggregateinfo, vectorlayer, regionidattr, regionlevel)
        else:
            logger.error('Vector layer file does not exist: %s' % vectorlayer)


        print (" \n  Results for Product  : {}".format(ecoagric_record["productcode"]))
        print ("  Results for Version  : {}".format(ecoagric_record["version"]))
        print ("  Results for Sprod    : {}".format(ecoagric_record["subproductcode"]))
        print ("  Results for date     : {}".format(ecoagric_record["product_date"]))
        print ("  Results for RegionLvl: {}".format(ecoagric_record["regionlevel"]))
        print ("  Results for RegionID : {}".format(ecoagric_record["regionid"]))
        print ("  Value is             : {}".format(ecoagric_record["tsvalue"]))

        self.assertAlmostEqual(ecoagric_record["tsvalue"],13.978191148171906)


    def test_PrecipVolume(self):

        productinfo = {
            "productcode": 'tamsat-rfe',
            "version": '2.0',
            "subproductcode": '10d',
            "mapsetcode": 'TAMSAT-Africa-4km'
        }

        startdate = '2017-01-01'
        enddate = '2018-05-01'

        aggregateinfo = {'aggregation_type': 'precip',
                         'aggregation_min': None,
                         'aggregation_max': None}

        vectorlayer = '/eStation2/layers/BEN_adm/BEN_adm1.shp'
        regionidattr = 'HASC_1'

        regionlevel = 'admin1'

        if os.path.isfile(vectorlayer):
            ecoagric_record = convert_to_ecoargis(productinfo, startdate, enddate, aggregateinfo, vectorlayer, regionidattr, regionlevel)
        else:
            logger.error('Vector layer file does not exist: %s' % vectorlayer)


        print (" \n  Results for Product  : {}".format(ecoagric_record["productcode"]))
        print ("  Results for Version  : {}".format(ecoagric_record["version"]))
        print ("  Results for Sprod    : {}".format(ecoagric_record["subproductcode"]))
        print ("  Results for date     : {}".format(ecoagric_record["product_date"]))
        print ("  Results for RegionLvl: {}".format(ecoagric_record["regionlevel"]))
        print ("  Results for RegionID : {}".format(ecoagric_record["regionid"]))
        print ("  Value is             : {}".format(ecoagric_record["tsvalue"]))

        self.assertAlmostEqual(ecoagric_record["tsvalue"],371.32997537572163)
