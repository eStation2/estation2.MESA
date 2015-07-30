# -*- coding: utf-8 -*-
from __future__ import absolute_import
__author__ = "Jurriaan van 't Klooster"


from unittest import TestCase
from lib.python import es_logging as log
# Trivial change
logger = log.my_logger(__name__)

from database import querydb
from lib.python import functions

class TestQuerydb(TestCase):
    def Test_set_thema(self):
        themaid = 'AGRYHMET'
        themaset = querydb.set_thema(themaid)
        print themaset

        self.assertEqual(True, themaset[0])

    def Test_get_i18n(self):

        i18n = querydb.get_i18n(lang='fra')
        len = i18n.__len__()
        print len
        for label, langtranslation in i18n:
            print label + ' ' + langtranslation

        self.assertEqual(1, 1)

    def Test_get_languages(self):

        languages = querydb.get_languages()
        logger.info("Languages active are: %s", languages)
        for language in languages:
            print language.langcode + ' ' + language.langdescription

        self.assertEqual(1, 1)

    def Test_get_timeseries_yaxes(self):
        products = [{"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10d", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10davg", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10dmax", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10dmin", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"vgt-ndvi", "version":"spot-v1", "subproductcode":"ndv", "mapsetcode":"SPOTV-Africa-1km"}]

        timeseries_yaxes = querydb.get_timeseries_yaxes(products)
        logger.info("Time series draw properties are: %s", timeseries_yaxes)
        axes = len(timeseries_yaxes)
        for timeseries_product in timeseries_yaxes:
            print timeseries_product.title

        self.assertEqual(1, 1)

    def Test_get_timeseries_drawproperties(self):

        product = {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10d"}
        timeseries_drawproperties = querydb.get_timeseries_drawproperties(product)
        logger.info("Time series draw properties are: %s", timeseries_drawproperties)
        for timeseries_product in timeseries_drawproperties:
            print timeseries_product.productcode

        self.assertEqual(1, 1)

    def Test_update_product_info(self):
        productinfo = {'productcode': 'chirp',
                       'version': 'undefined',
                       'orig_productcode': 'chirpchanged',
                       'orig_version': 'undefined'}

        update_product = querydb.update_product_info(productinfo)

        print update_product

    def Test_get_eumetcastsources(self):
        eumetcastsources = querydb.get_eumetcastsources()

        if eumetcastsources.__len__() > 0:
            for row in eumetcastsources:
                row_dict = functions.row2dict(row)

    def Test_get_internetsources(self):
        internetsources = querydb.get_internetsources()

        if internetsources.__len__() > 0:
            for row in internetsources:
                row_dict = functions.row2dict(row)

    def Test_get_i18n(self):

        i18n = querydb.get_i18n(lang='fra')
        len = i18n.__len__()
        print len
        for label, langtranslation in i18n:
            print label + ' ' + langtranslation

        self.assertEqual(1, 1)

    def Test_get_languages(self):

        languages = querydb.get_languages()
        logger.info("Languages active are: %s", languages)
        for language in languages:
            print language.langcode + ' ' + language.langdescription

        self.assertEqual(1, 1)

    def Test_get_timeseries_yaxes(self):
        products = [{"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10d", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10davg", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10dmax", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10dmin", "mapsetcode":"FEWSNET-Africa-8km"},
                    {"productcode":"vgt-ndvi", "version":"spot-v1", "subproductcode":"ndv", "mapsetcode":"SPOTV-Africa-1km"}]

        timeseries_yaxes = querydb.get_timeseries_yaxes(products)
        logger.info("Time series draw properties are: %s", timeseries_yaxes)
        axes = len(timeseries_yaxes)
        for timeseries_product in timeseries_yaxes:
            print timeseries_product.title

        self.assertEqual(1, 1)

    def Test_get_timeseries_drawproperties(self):

        product = {"productcode":"fewsnet-rfe", "version":"2.0", "subproductcode":"10d"}
        timeseries_drawproperties = querydb.get_timeseries_drawproperties(product)
        logger.info("Time series draw properties are: %s", timeseries_drawproperties)
        for timeseries_product in timeseries_drawproperties:
            print timeseries_product.productcode

        self.assertEqual(1, 1)

    def Test_get_timeseries_subproducts(self):
        timeseries_subproducts = querydb.get_timeseries_subproducts(productcode='fewsnet-rfe',
                                                                    subproductcode='10d',
                                                                    version='2.0')
        logger.info("Time series products are: %s", timeseries_subproducts)
        for timeseries_product in timeseries_subproducts:
            print timeseries_product

        self.assertEqual(1, 1)

    def Test_get_timeseries_products(self):
        timeseries_products = querydb.get_timeseries_products()
        logger.info("Time series products are: %s", timeseries_products)
        for timeseries_product in timeseries_products:
            print timeseries_product

        self.assertEqual(1, 1)

    def Test_get_active_internet_sources(self):
        internet_sources = querydb.get_active_internet_sources()
        logger.info("Internet sources are: %s", internet_sources)
        for internet_source in internet_sources:
            print internet_source.url

        self.assertEqual(1, 1)

    def Test_get_eumetcast_sources(self):

        eumetcast_sources = querydb.get_eumetcast_sources()
        logger.info("Eumetcast sources are: %s", eumetcast_sources)
        for row in eumetcast_sources:
            print row

        self.assertEqual(1, 1)

    def Test_get_datasource_descr(self):

        datasource_descr = querydb.get_datasource_descr(source_type='EUMETCAST',
                                                        source_id='EO:EUM:DAT:SPOT:S10NDVI')
        logger.info("Eumetcast source description is: %s", datasource_descr)
        for row in datasource_descr:
            print row

        datasource_descr = querydb.get_datasource_descr(source_type='INTERNET',
                                                        source_id='USGS:EARLWRN:FEWSNET')
        logger.info("Internet source description is: %s", datasource_descr)
        for row in datasource_descr:
            print row

        self.assertEqual(1, 1)

    def Test_get_product_sources(self):

        product_sources = querydb.get_product_sources(productcode='fewsnet-rfe',
                                                      subproductcode='fewsnet-rfe_native',
                                                      version='undefined')
        logger.info("Product sources are: %s", product_sources)
        for row in product_sources:
            print row

        self.assertEqual(1, 1)

    def Test_get_product_sources2(self):

        product_sources = querydb.get_product_sources(productcode='vgt-ndvi',
                                                      subproductcode='vgt-ndvi_native',
                                                      version='spot-v1')
        logger.info("Product sources are: %s", product_sources)
        for row in product_sources:
            print row

        self.assertEqual(1, 1)

    def Test_get_ingestion_subproduct(self):

        ingestion_subproduct = querydb.get_ingestion_subproduct(productcode='vgt_ndvi',
                                                                version='undefined')
        logger.info("All ingestions of product are: %s", ingestion_subproduct)
        for row in ingestion_subproduct:
            print row

        self.assertEqual(1, 1)

    def Test_get_ingestion_product(self):

        ingestion_product = querydb.get_ingestion_product(productcode='vgt_ndvi',
                                                          version='undefined')
        logger.info("Active ingestions of product are: %s", ingestion_product)
        for row in ingestion_product:
            print row

        self.assertEqual(1, 1)

    def Test_get_mapset(self):

        mapset = querydb.get_mapset(mapsetcode='WGS84_Africa_1km')
        logger.info("Mapset: %s", mapset)

        self.assertEqual(1, 1)

    def Test_get_internet(self):

        internet = querydb.get_internet(internet_id='USGS:EARLWRN:FEWSNET')
        logger.info("Internet source info: %s", internet)

        self.assertEqual(1, 1)

    def Test_get_eumetcast(self):

        eumetcast = querydb.get_eumetcast(source_id='EO:EUM:DAT:SPOT1:S10NDVI')
        logger.info("Eumetcast source info: %s", eumetcast)

        self.assertEqual(1, 1)

    def Test_get_product_native(self):

        product = querydb.get_product_native(productcode='fewsnet_rfe')
        logger.info("Native product info: %s", product)

        self.assertEqual(1, 1)

    def Test_get_product_in_info(self):

        product_in = querydb.get_product_in_info(productcode='fewsnet-rfe',
                                                 subproductcode='10d',
                                                 version='undefined',
                                                 datasource_descr_id='USGS:EARLWRN:FEWSNET')
        logger.info("Product IN info: %s", product_in)

        self.assertEqual(1, 1)

    def Test_get_product_in_info1(self):

        product_in = querydb.get_product_in_info(productcode='vgt-ndvi',
                                                 subproductcode='ndv',
                                                 version='spot-v1',
                                                 datasource_descr_id='EO:EUM:DAT:SPOT1:S10NDVI')
        logger.info("Product IN info: %s", product_in)

        self.assertEqual(1, 1)

    def Test_get_product_in_info2(self):

        product_in = querydb.get_product_in_info(productcode='modis-firms',
                                                 subproductcode='1day',
                                                 version='v5.0',
                                                 datasource_descr_id='FIRMS:NASA')
        logger.info("Product IN info: %s", product_in)

        self.assertEqual(1, 1)

    def Test_get_product_in_info3(self):

        product_in = querydb.get_product_in_info(productcode='modis-chla',
                                                 subproductcode='chla-day',
                                                 version='v2013.1',
                                                 datasource_descr_id='GSFC:CGI:MODIS:CHLA:1D')
        logger.info("Product IN info: %s", product_in)

        self.assertEqual(1, 1)


    def Test_get_product_out_info(self):

        product_out = querydb.get_product_out_info(productcode='fewsnet-rfe',
                                                   subproductcode='10d',
                                                   version='2.0')
        logger.info("Product OUT info: %s", product_out)
        for row in product_out:
            print row

        self.assertEqual(1, 1)
        self.assertEqual(1, 1)

    def Test_get_products_acquisition(self):

        product = querydb.get_products_acquisition(activated=True)
        logger.info("Active products: %s", product)
        for row in product:
            print row

        product = querydb.get_products_acquisition(activated=False)
        logger.info("Non active products: %s", product)
        for row in product:
            print row

    def Test_get_products(self):

        product = querydb.get_products(activated=True)
        logger.info("Active products: %s", product)
        for row in product:
            print row

        product = querydb.get_products(activated=False)
        logger.info("Non active products: %s", product)
        for row in product:
            print row

        product = querydb.get_products(masked=False)
        logger.info("Not masked products: %s", product)
        for row in product:
            print row

        self.assertEqual(1, 1)

    def Test_get_subproduct(self):

        subproduct = querydb.get_subproduct(productcode='vgt-ndvi',
                                            subproductcode='ndv',
                                            version='spot-v1')
        logger.info("Subproduct: %s", subproduct)

        self.assertEqual(1, 1)

    def Test_get_dataacquisitions(self):

        dataacquisitions = querydb.get_dataacquisitions()
        logger.info("All Data Acquisitions: %s", dataacquisitions)
        for row in dataacquisitions:
            print row

        self.assertEqual(1, 1)

    def Test_get_ingestions(self):

        ingestions = querydb.get_ingestions()
        logger.info("All Ingestions: %s", ingestions)
        for row in ingestions:
            print row

        self.assertEqual(1, 1)

    def Test_get_legend_info(self):

        legend_info = querydb.get_legend_info(legendid=6)
        logger.info("Legend info: %s", legend_info)
        if legend_info.__len__() > 0:
            for row in legend_info:
                print row

        self.assertEqual(1, 1)

    def Test_get_legend_steps(self):

        legend_steps = querydb.get_legend_steps(legendid=6)
        logger.info("Legend info: %s", legend_steps)
        for row in legend_steps:
            color_rgb = row.color_rgb
            print color_rgb.split(' ')

        self.assertEqual(1, 1)

    def Test_get_product_legends(self):

        product_legends = querydb.get_product_legends(productcode='vgt-ndvi', subproductcode='ndv', version='spot-v1')
        logger.info("Product Legends: %s", product_legends)
        for row in product_legends:
            print row

        self.assertEqual(1, 1)

    def Test_get_processing_chains(self):

        processing_chains = querydb.get_processing_chains()
        logger.info("Processing chains: %s", processing_chains)
        for row in processing_chains:
            print row.algorithm
            print row.output_mapsetcode

        self.assertEqual(1, 1)

    def Test_get_processingchains_input_products(self):
        import json
        processingchain_products = querydb.get_processingchains_input_products()
        if processingchain_products.__len__() > 0:
            products_dict_all = []

            # loop the products list
            for input_product in processingchain_products:
                process_id = input_product.process_id
                output_mapsetcode = input_product.output_mapsetcode
                prod_dict = functions.row2dict(input_product)
                # prod_dict = input_product
                # del prod_dict['_labels']

                prod_dict['productmapsets'] = []
                mapset_info = querydb.get_mapset(mapsetcode=output_mapsetcode)

                mapset_dict = functions.row2dict(mapset_info)
                mapset_dict['mapsetoutputproducts'] = []
                output_products = querydb.get_processingchain_output_products(process_id)
                for outputproduct in output_products:
                    outputproduct_dict = functions.row2dict(outputproduct)
                    # outputproduct_dict = outputproduct
                    # del outputproduct_dict['_labels']
                    mapset_dict['mapsetoutputproducts'].append(outputproduct_dict)
                prod_dict['productmapsets'].append(mapset_dict)
                products_dict_all.append(prod_dict)

            prod_json = json.dumps(products_dict_all,
                                   ensure_ascii=False,
                                   sort_keys=True,
                                   indent=4,
                                   separators=(', ', ': '))

        # logger.info("Processing chains: %s", processingchain_products)
        # for row in processingchain_products:
        #     logger.info("row.dict: %s", row.__dict__)
        #     logger.info("row.process_id: %s", row.process_id)
        #     logger.info("row.output_mapsetcode: %s", row.output_mapsetcode)
        #     logger.info("row.mapsetcode: %s", row.mapsetcode)
        #     print row.process_id
        #     print row.output_mapsetcode
        #     print row.mapsetcode

        self.assertEqual(1, 1)

    def Test_get_processingchain_output_products(self):
        process_id = 1
        processingchain_output_products = querydb.get_processingchain_output_products(process_id)
        logger.info("Processing chains: %s", processingchain_output_products)
        for row in processingchain_output_products:
            logger.info("row.productcode: %s", row.productcode)
            logger.info("row.subproductcode: %s", row.subproductcode)
            print row.productcode
            print row.subproductcode

        self.assertEqual(1, 1)

    def Test_get_active_processing_chains(self):

        processing_chains = querydb.get_active_processing_chains()
        logger.info("Active processing chains: %s", processing_chains)
        for row in processing_chains:
            print 'ID= '+str(row.process_id)
            print 'Module:Method= '+row.algorithm + ':'+ row.derivation_method


        self.assertEqual(1, 1)

    def Test_get_processing_chain_inputs(self):

        process_id = 4
        input_products = querydb.get_processing_chain_products(process_id,type='input')
        logger.info("Processing chains id:%s", process_id)
        for row in input_products:
            print 'Product Code     = '+str(row.productcode)
            print 'Subproduct Code  = '+str(row.subproductcode)
            print 'Version          = '+str(row.version)
            print 'Mapset           = '+str(row.mapsetcode)


        self.assertEqual(1, 1)

    def Test_get_processing_chain_outputs(self):

        process_id = 4
        output_products = querydb.get_processing_chain_products(process_id, type='output')
        logger.info("Processing chains id:%s", process_id)
        for row in output_products:
            print 'Product Code     = '+str(row.productcode)
            print 'Subproduct Code  = '+str(row.subproductcode)
            print 'Version          = '+str(row.version)
            print 'Mapset           = '+str(row.mapsetcode)

        self.assertEqual(1, 1)

    # def Test_update_processing_chain_products(self):
    #
    #     process_id = 4
    #     productcode='vgt-ndvi'
    #     version='sv2-pv2.1'
    #     subproductcode='10dmax'
    #     mapsetcode='SPOTV-Africa-1km'
    #     activated=True
    #     final=False
    #     output_products = querydb.update_processing_chain_products(process_id,
    #                                                                productcode,
    #                                                                version,
    #                                                                subproductcode,
    #                                                                mapsetcode,
    #                                                                activated,
    #                                                                final)

        # self.assertEqual(1, 1)