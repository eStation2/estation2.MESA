# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from lib.python import es_logging as log
logger = log.my_logger(__name__)

__author__ = "Jurriaan van 't Klooster"

from database import querydb

#db = querydb.connect_db()

products = querydb.get_products(echo=True)
print products


#class TestQuerydb(unittest.TestCase):
#
#    def Test_get_active_internet_sources(self):
#
#        internet_sources = querydb.get_active_internet_sources()
#        logger.info("Internet sources are: %s", internet_sources)
#        for internet_source in internet_sources:
#            print internet_source.url
#
#        self.assertEqual(1,1)
    #
    # def test_querydb(self):
    #     product = 'vgt_ndvi'
    #     subproduct = 'ndv'
    #     pkey = {"productcode": product, "subproductcode": subproduct}
    #     product_info = querydb.get_product_out_info(echo=False, **pkey)
    #     product_out_params = {"out_data_type": product_info.data_type_id,
    #                           "out_scale_factor": product_info.scale_factor,
    #                           "out_scale_offset": product_info.scale_offset,
    #                           "out_nodata": product_info.nodata}
    #
    #     #print product_out_params
    #
    #
    #     args = {"productcode": product,
    #             "subproductcode": subproduct,
    #             "datasource_descr_id": 'EO:EUM:DAT:SPOT:S10NDVI'}
    #     product_in_info = querydb.get_product_in_info(echo=False, **args)
    #     product_in_params = {"in_data_type": product_in_info.data_type_id,
    #                          "in_scale_factor": product_in_info.scale_factor,
    #                          "in_scale_offset": product_in_info.scale_offset,
    #                          "in_nodata": product_in_info.no_data,
    #                          "in_mask_min": product_in_info.scale_offset,
    #                          "in_mask_max": product_in_info.scale_offset}
    #

