# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from future import standard_library
from builtins import str

import unittest
from unittest import TestCase

from lib.python import es_logging as log
from database import querydb
from lib.python import functions
from database import crud
from database import connectdb
from config import es_constants

standard_library.install_aliases()

logger = log.my_logger(__name__)

dbschema_products = connectdb.ConnectDB(schema='products').db
dbschema_analysis = connectdb.ConnectDB(schema='analysis').db

crud_db_analysis = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])
crud_db_products = crud.CrudDB(schema=es_constants.es2globals['schema_products'])

PRINT_RESULTS = False


def print_rows(result):
    if PRINT_RESULTS:
        for row in result:
            print(row)


class TestQuerydb(TestCase):

    def test_activate_deactivate_product(self):
        productcode = 'chirps-dekad'
        version = '2.0'
        activate = False

        result = querydb.activate_deactivate_product(productcode=productcode, version=version, activate=activate)
        self.assertTrue(result)

        activate = True
        result = querydb.activate_deactivate_product(productcode=productcode, version=version, activate=activate)
        self.assertTrue(result)

    def test_checklogin(self):
        params = {
            'username': 'adminuser',
            'password': 'mesadmin'
        }
        p = functions.dotdict(params)

        result = querydb.checklogin(p)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_checkUser(self):
        params = {
            'userid': 'adminuser'
        }
        result = querydb.checkUser(params)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = None because adminuser does not exist!

    def test_copylegend(self):
        legendid = 6
        legend_descriptive_name = 'My NDVI'

        result = querydb.copylegend(legendid=legendid, legend_descriptive_name=legend_descriptive_name)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertNotEqual(result, legendid)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        # delete new copied legend
        legend = {
            'legend_id': result
        }
        crud_db_analysis.delete('legend', **legend)

    def test_createlegend(self):
        params = {
            'legend_name': 'TEST CREATE LEGEND',
            'min_value': -0.2,
            'max_value': 1,
            'colorbar': 'TEST LEGEND'
        }

        result = querydb.createlegend(params)
        if result != -1:
            if PRINT_RESULTS:
                print(result)
            self.assertIsInstance(result, int)
        else:
            self.assertFalse(True)  # Test fails: result = -1 because of an exception error!

        # delete created legend
        legend = {
            'legend_id': result
        }
        crud_db_analysis.delete('legend', **legend)

    def test_deletelegendsteps(self):
        legendid = 6
        legend_descriptive_name = 'My NDVI'
        newlegendid = querydb.copylegend(legendid=legendid, legend_descriptive_name=legend_descriptive_name)

        result = querydb.deletelegendsteps(str(newlegendid))
        self.assertEqual(result, True)

        # delete new copied legend
        legend = {
            'legend_id': newlegendid
        }
        crud_db_analysis.delete('legend', **legend)

    def test_export_legend_steps(self):
        legendid = 6

        result = querydb.export_legend_steps(legendid=legendid)
        if result:
            print_rows(result)
            self.assertEqual(result.__len__(), 12)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_active_internet_sources(self):
        result = querydb.get_active_internet_sources()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_active_processing_chains(self):
        result = querydb.get_active_processing_chains()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_active_subdatasource_descriptions(self):
        result = querydb.get_active_subdatasource_descriptions()
        if result.__len__() > 0:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_all_legends(self):
        result = querydb.get_all_legends()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_categories(self):
        allrecs = True

        result1 = querydb.get_categories(allrecs=allrecs)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        allrecs = False
        result2 = querydb.get_categories(allrecs=allrecs)
        if result2:
            print_rows(result2)
            self.assertLess(result2.__len__(), result1.__len__())
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_dataacquisitions(self):
        result = querydb.get_dataacquisitions()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_datasource_descr(self):
        result1 = querydb.get_datasource_descr(source_type='EUMETCAST', source_id='EO:EUM:DAT:PROBA-V2.0:FAPAR')
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_datasource_descr(source_type='INTERNET', source_id='UCSB:CHIRPS:DEKAD:2.0')
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_datatypes(self):
        result = querydb.get_datatypes()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_dateformats(self):
        result = querydb.get_dateformats()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_enabled_ingest_derived_of_product(self):
        productcode = 'vgt-dmp'
        version = 'V2.0'
        mapsetcode = 'SPOTV-Africa-1km'
        result1 = querydb.get_enabled_ingest_derived_of_product(productcode=productcode,
                                                                version=version,
                                                                mapsetcode=mapsetcode)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result1 = False because of an exception error!

        mapsetcode = None
        result2 = querydb.get_enabled_ingest_derived_of_product(productcode=productcode,
                                                                version=version,
                                                                mapsetcode=mapsetcode)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result2 = False because of an exception error!

    def test_get_eumetcast(self):
        source_id = 'EO:EUM:DAT:PROBA-V2.0:FAPAR'
        allrecs = False
        result1 = querydb.get_eumetcast(source_id=source_id, allrecs=allrecs)
        if result1:
            print_rows(result1)
            self.assertEqual(result1[0]['eumetcast_id'], source_id)
        else:
            self.assertFalse(True)  # Test fails: result1 = False because of an exception error!

        allrecs = True
        result2 = querydb.get_eumetcast(source_id=source_id, allrecs=allrecs)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result2 = False because of an exception error!

    def test_get_eumetcast_sources(self):
        result = querydb.get_eumetcast_sources()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_eumetcastsources(self):
        result = querydb.get_eumetcastsources()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_frequencies(self):
        result = querydb.get_frequencies()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_frequency(self):
        frequency_id = 'e1dekad'
        result = querydb.get_frequency(frequency_id=frequency_id)
        if result:
            print_rows(result)
            self.assertEqual(result.frequency_id, frequency_id)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_graph_drawproperties(self):
        params = {
            'userid': '',
            'graph_tpl_id': '',
            'graphtype': 'xy'
        }
        p = functions.dotdict(params)
        result1 = querydb.get_graph_drawproperties(p)
        if result1:
            print_rows(result1)
            self.assertEqual(result1.__len__(), 1)
        else:
            self.assertFalse(True)  # Test fails: result1 = False because of an exception error!

        query = "SELECT graph_tpl_id FROM analysis.user_graph_templates where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        graph_tpl_id = queryresult[0]['graph_tpl_id']
        params = {
            'userid': 'jrc_ref',
            'graph_tpl_id': str(graph_tpl_id),
            'graphtype': 'xy'
        }
        p = functions.dotdict(params)
        result2 = querydb.get_graph_drawproperties(p)

        if result2:
            print_rows(result2)
            self.assertEqual(result2.__len__(), 1)
        else:
            self.assertFalse(True)  # Test fails: result2 = False because of an exception error!

    def test_get_graph_tsdrawprops(self):
        query = "SELECT graph_tpl_id FROM analysis.user_graph_templates where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        graph_tpl_id = queryresult[0]['graph_tpl_id']
        result = querydb.get_graph_tsdrawprops(graph_tpl_id=graph_tpl_id)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_graph_yaxes(self):
        query = "SELECT graph_tpl_id FROM analysis.user_graph_templates where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        graph_tpl_id = queryresult[0]['graph_tpl_id']
        result = querydb.get_graph_yaxes(graph_tpl_id=graph_tpl_id)
        if result:
            print_rows(result)
            self.assertEqual(result.__len__(), 1)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_i18n(self):
        result = querydb.get_i18n(lang='fra')
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_ingestion_product(self):
        allrecs = True
        productcode = 'vgt-fcover'
        version = 'V2.0'
        result1 = querydb.get_ingestion_product(allrecs=allrecs)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result1 = False because of an exception error!

        result2 = querydb.get_ingestion_product(productcode=productcode, version=version)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result2 = False because of an exception error!

    def test_get_ingestion_subproduct(self):
        allrecs = True
        productcode = 'vgt-fcover'
        version = 'V2.0'
        result1 = querydb.get_ingestion_subproduct(allrecs=allrecs)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result1 = False because of an exception error!

        result2 = querydb.get_ingestion_subproduct(productcode=productcode, version=version)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result2 = False because of an exception error!

    def test_get_ingestions(self):
        result = querydb.get_ingestions()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_ingestsubproducts(self):
        result = querydb.get_ingestsubproducts()
        if result.__len__() > 0:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_internet(self):
        internet_id = 'UCSB:CHIRPS:DEKAD:2.0'
        result = querydb.get_internet(internet_id=internet_id)  # This query is not used anywhere in the code!
        if result:
            print_rows(result)
            self.assertEqual(result[0].internet_id, internet_id)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_internetsources(self):
        result = querydb.get_internetsources()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_languages(self):
        result = querydb.get_languages()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_last_graph_tpl_id(self):
        userid = 'jrc_ref'
        query = "SELECT workspaceid FROM analysis.user_workspaces where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        workspaceid = queryresult[0]['workspaceid']
        result = querydb.get_last_graph_tpl_id(userid=userid, workspaceid=workspaceid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_last_map_tpl_id(self):
        userid = 'jrc_ref'
        query = "SELECT workspaceid FROM analysis.user_workspaces where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        workspaceid = queryresult[0]['workspaceid']
        result = querydb.get_last_map_tpl_id(userid=userid, workspaceid=workspaceid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_layers(self):
        result = querydb.get_layers()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_legend_assigned_datasets(self):
        legendid = 1
        result = querydb.get_legend_assigned_datasets(legendid=legendid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_legend_info(self):
        legendid = 1
        result = querydb.get_legend_info(legendid=legendid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_legend_steps(self):
        legendid = 1
        result = querydb.get_legend_steps(legendid=legendid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_legend_totals(self):
        legendid = 1
        result = querydb.get_legend_totals(legendid=legendid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_logos(self):
        result = querydb.get_logos()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_mapset(self):
        allrecs = True
        mapsetcode = 'SPOTV-Africa-1km'
        result1 = querydb.get_mapset(allrecs=allrecs)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result1 = False because of an exception error!

        result2 = querydb.get_mapset(mapsetcode=mapsetcode)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result2 = False because of an exception error!

    def test_get_mapsets(self):
        result = querydb.get_mapsets()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_mapsets_for_ingest(self):
        params = {
            'productcode': 'vgt-dmp',
            'version': 'V2.0',
            'subproductcode': 'dmp'
        }
        # Get all the mapsets that are not already defined for the subproduct for ingestion.
        result = querydb.get_mapsets_for_ingest(productcode=params['productcode'], version=params['version'],
                                                subproductcode=params['subproductcode'])
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_predefined_bboxes(self):
        result = querydb.get_predefined_bboxes()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_processing_chain_products(self):
        process_id = 4
        input_products = querydb.get_processing_chain_products(process_id, type='input')
        # logger.info("Processing chains id:%s", process_id)
        if input_products:
            print_rows(input_products)
            self.assertGreater(input_products.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        output_products = querydb.get_processing_chain_products(process_id, type='output')
        if output_products:
            print_rows(output_products)
            self.assertGreater(output_products.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        input_output_products = querydb.get_processing_chain_products(process_id, type='All')
        if input_output_products:
            print_rows(input_output_products)
            self.assertGreater(input_output_products.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_processing_chains(self):
        result = querydb.get_processing_chains()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_processingchain_output_products(self):
        process_id = 1
        result = querydb.get_processingchain_output_products(process_id)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_processingchains_input_products(self):
        process_id = 1
        result1 = querydb.get_processingchains_input_products(process_id)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        process_id = None
        result2 = querydb.get_processingchains_input_products(process_id)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 1)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_active_derived_mapsets(self):
        params = {
            'productcode': 'vgt-ndvi',
            'subproductcode': 'ndvi-linearx2',
            'version': 'sv2-pv2.2'
        }
        result = querydb.get_product_active_derived_mapsets(productcode=params['productcode'],
                                                            version=params['version'],
                                                            subproductcode=params['subproductcode'])
        if result.__len__() > 0:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_product_active_ingest_mapsets(self):
        params = {
            'productcode': 'vgt-dmp',
            'subproductcode': 'dmp',
            'version': 'V2.0'
        }
        result = querydb.get_product_active_ingest_mapsets(productcode=params['productcode'],
                                                           version=params['version'],
                                                           subproductcode=params['subproductcode'])
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_product_active_mapsets(self):
        params = {
            'productcode': 'vgt-ndvi',
            'version': 'sv2-pv2.2'
        }
        # Query not used anymore!
        result = querydb.get_product_active_mapsets(productcode=params['productcode'], version=params['version'])
        if result.__len__() > 0:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_product_default_legend_steps(self):
        params = {
            'productcode': 'vgt-ndvi',
            'subproductcode': 'ndvi-linearx2',
            'version': 'sv2-pv2.2'
        }
        result = querydb.get_product_default_legend_steps(productcode=params['productcode'],
                                                          version=params['version'],
                                                          subproductcode=params['subproductcode'])
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_in_info(self):
        params = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': '10d',
            'version': '2.0',
            'datasource_descr_id': 'USGS:EARLWRN:FEWSNET'
        }
        result = querydb.get_product_in_info(**params)
        if result.datasource_descr_id == 'USGS:EARLWRN:FEWSNET':
            if PRINT_RESULTS:
                print(result)
            self.assertTrue(True)   # Test OK
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

        # product_in = querydb.get_product_in_info(productcode='vgt-ndvi',
        #                                          subproductcode='ndv',
        #                                          version='spot-v1',
        #                                          datasource_descr_id='EO:EUM:DAT:SPOT1:S10NDVI')
        #
        # product_in = querydb.get_product_in_info(productcode='modis-firms',
        #                                          subproductcode='1day',
        #                                          version='v5.0',
        #                                          datasource_descr_id='FIRMS:NASA')
        #
        # product_in = querydb.get_product_in_info(productcode='modis-chla',
        #                                          subproductcode='chla-day',
        #                                          version='v2013.1',
        #                                          datasource_descr_id='GSFC:CGI:MODIS:CHLA:1D')
        # product_in = querydb.get_product_in_info(productcode='lsasaf-et',
        #                                          subproductcode='et',
        #                                          version='undefined',
        #                                          datasource_descr_id='EO:EUM:DAT:MSG:ET-SEVIRI')

    def test_get_product_legends(self):
        params = {
            'productcode': 'vgt-ndvi',
            'subproductcode': 'ndv',
            'version': 'spot-v1'
        }
        result = querydb.get_product_legends(**params)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_native(self):
        # productcode = 'vgt-lai'
        # version = 'V2.0'
        params = {
            'productcode': 'fewsnet-rfe',
            'version': '2.0'
        }
        result1 = querydb.get_product_native(**params)
        if result1.__len__() > 0:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

        result2 = querydb.get_product_native(allrecs=True)
        if result2.__len__() > 0:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_product_out_info(self):
        params = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': '10d',
            'version': '2.0'
        }
        result1 = querydb.get_product_out_info(**params)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_product_out_info(allrecs=True)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_out_info_connect(self):
        params = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': '10d',
            'version': '2.0'
        }
        result1 = querydb.get_product_out_info_connect(**params)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_product_out_info_connect(allrecs=True)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_sources(self):
        # product_sources = querydb.get_product_sources(productcode='vgt-ndvi',
        #                                               subproductcode='vgt-ndvi_native',
        #                                               version='spot-v1')
        params = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': 'fewsnet-rfe_native',
            'version': '2.0'
        }
        result = querydb.get_product_sources(**params)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_subproducts(self):
        params = {
            'productcode': 'fewsnet-rfe',
            'version': '2.0'
        }
        result = querydb.get_product_subproducts(**params)
        if result.__len__() > 0:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_product_timeseries_drawproperties(self):
        product = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': '10d',
            'version': '2.0'
        }
        userid = 'jrc_ref'
        istemplate = 'false'
        graph_type = 'xy'
        graph_tpl_id = '-1'
        graph_tpl_name = 'default'

        result1 = querydb.get_product_timeseries_drawproperties(product)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_product_timeseries_drawproperties(product,
                                                                userid=userid,
                                                                istemplate=istemplate,
                                                                graph_type=graph_type,
                                                                graph_tpl_id=graph_tpl_id,
                                                                graph_tpl_name=graph_tpl_name
                                                                )
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_product_yaxe(self):
        product = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': '10d',
            'version': '2.0'
        }
        userid = 'jrc_ref'
        istemplate = 'false'
        graph_type = 'xy'
        graph_tpl_id = '-1'
        graph_tpl_name = 'default'

        result1 = querydb.get_product_yaxe(product)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_product_yaxe(product,
                                           userid=userid,
                                           istemplate=istemplate,
                                           graph_type=graph_type,
                                           graph_tpl_id=graph_tpl_id,
                                           graph_tpl_name=graph_tpl_name
                                           )
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_products(self):
        result1 = querydb.get_products(activated=True)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_products(activated=False)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result3 = querydb.get_products(activated=True, masked=False)
        if result3:
            print_rows(result3)
            self.assertGreater(result3.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result4 = querydb.get_products(activated=True, masked=True)
        if result4:
            print_rows(result4)
            self.assertGreater(result4.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_products_acquisition(self):
        result1 = querydb.get_products_acquisition(activated=True)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_products_acquisition(activated=False)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result3 = querydb.get_products_acquisition(activated=None)
        if result3:
            print_rows(result3)
            self.assertGreater(result3.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_projections(self):
        result = querydb.get_projections()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_resolutions(self):
        result = querydb.get_resolutions()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_spirits(self):
        result = querydb.get_spirits()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_subproduct(self):
        params = {
            'productcode': 'vgt-ndvi',
            'subproductcode': 'ndv',
            'version': 'spot-v1'
        }
        result1 = querydb.get_subproduct(**params)
        if result1.subproductcode == 'ndv':
            if PRINT_RESULTS:
                print(result1)
            self.assertTrue(True)   # Test OK
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

        result2 = querydb.get_subproduct(**params, masked=True)
        # Subproduct ndv of vgt-ndvi spot-v1 is not masked so result2 gives None back.
        if result2 is None:
            self.assertTrue(True)   # Test OK
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_thema_products(self):
        result = querydb.get_thema_products(thema='JRC')
        if result.__len__() > 0:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = [] because of an exception error!

    def test_get_themas(self):
        result = querydb.get_themas()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_timeseries_drawproperties(self):
        params = {
            'userid': 'jrc_ref',
            'istemplate': 'false',
            'graph_tpl_id': '-1',
            'graph_tpl_name': 'default',
            'graph_type': 'xy'
        }
        p = functions.dotdict(params)
        result1 = querydb.get_timeseries_drawproperties(p)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        params = {}
        result2 = querydb.get_timeseries_drawproperties(params)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_timeseries_products(self):
        result1 = querydb.get_timeseries_products()
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_timeseries_products(masked=True)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result3 = querydb.get_timeseries_products(masked=False)
        if result3:
            print_rows(result3)
            self.assertGreater(result3.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_timeseries_subproducts(self):
        params = {
            'productcode': 'fewsnet-rfe',
            'subproductcode': '10d',
            'version': '2.0'
        }
        result1 = querydb.get_timeseries_subproducts(**params)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_timeseries_subproducts(**params, masked=False)
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result3 = querydb.get_timeseries_subproducts(**params, masked=True)
        # There are no masked subproducts
        if result3.__len__() == 0:
            self.assertTrue(True)  # Test OK
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_timeseries_yaxes(self):
        products = [{"productcode": "fewsnet-rfe", "version": "2.0", "subproductcode": "10d",
                     "mapsetcode": "FEWSNET-Africa-8km"},
                    {"productcode": "fewsnet-rfe", "version": "2.0", "subproductcode": "10davg",
                     "mapsetcode": "FEWSNET-Africa-8km"},
                    {"productcode": "fewsnet-rfe", "version": "2.0", "subproductcode": "10dmax",
                     "mapsetcode": "FEWSNET-Africa-8km"},
                    {"productcode": "fewsnet-rfe", "version": "2.0", "subproductcode": "10dmin",
                     "mapsetcode": "FEWSNET-Africa-8km"},
                    {"productcode": "vgt-ndvi", "version": "spot-v1", "subproductcode": "ndv",
                     "mapsetcode": "SPOTV-Africa-1km"}]
        userid = 'jrc_ref'
        istemplate = 'false'
        graph_type = 'xy'
        graph_tpl_id = '-1'
        graph_tpl_name = 'default'

        result1 = querydb.get_timeseries_yaxes(products)
        if result1:
            print_rows(result1)
            self.assertGreater(result1.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        result2 = querydb.get_timeseries_yaxes(products,
                                               userid=userid,
                                               istemplate=istemplate,
                                               graph_type=graph_type,
                                               graph_tpl_id=graph_tpl_id,
                                               graph_tpl_name=graph_tpl_name
                                               )
        if result2:
            print_rows(result2)
            self.assertGreater(result2.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_user_graph_templates(self):
        userid = 'jrc_ref'
        result = querydb.get_user_graph_templates(userid=userid)
        # ToDO: create some graph templated for the user jrc_ref!
        if result.__len__() >= 0:
            print_rows(result)
            self.assertGreaterEqual(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_user_map_templates(self):
        userid = 'jrc_ref'
        result = querydb.get_user_map_templates(userid=userid)
        # ToDO: create some map templated for the user jrc_ref!
        if result.__len__() >= 0:
            print_rows(result)
            self.assertGreaterEqual(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_user_workspaces(self):
        userid = 'jrc_ref'
        result = querydb.get_user_workspaces(userid=userid)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_workspace_graphs(self):
        query = "SELECT workspaceid FROM analysis.user_workspaces where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        workspaceid = queryresult[0]['workspaceid']
        params = {
            'workspaceid': workspaceid,
            'userid': 'jrc_ref'
        }
        result = querydb.get_workspace_graphs(**params)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_get_workspace_maps(self):
        query = "SELECT workspaceid FROM analysis.user_workspaces where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        workspaceid = queryresult[0]['workspaceid']
        params = {
            'workspaceid': workspaceid,
            'userid': 'jrc_ref'
        }
        result = querydb.get_workspace_maps(**params)
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_getCreatedUserWorkspace(self):
        query = "SELECT workspacename FROM analysis.user_workspaces where userid = 'jrc_ref' LIMIT 1"
        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        workspacename = queryresult[0]['workspacename']
        userid = 'jrc_ref'

        result = querydb.getCreatedUserWorkspace(userid, workspacename)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertIsNot(result, -1)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_getDefaultUserGraphTemplateID(self):
        userid = 'jrc_ref'
        istemplate = False
        graph_type = 'xy'
        graph_tpl_name = 'default'

        result = querydb.getDefaultUserGraphTemplateID(userid=userid,
                                                       istemplate=istemplate,
                                                       graph_type=graph_type,
                                                       graph_tpl_name=graph_tpl_name
                                                       )
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertIsInstance(result, int)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_getDefaultUserWorkspaceID(self):
        userid = 'jrc_ref'
        result = querydb.getDefaultUserWorkspaceID(userid=userid)   # returns defaultworkspaceid as a string
        if result:
            print_rows(result)
            self.assertIsInstance(int(result), int)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_getusers(self):
        result = querydb.getusers()
        if result:
            print_rows(result)
            self.assertGreater(result.__len__(), 0)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_set_thema(self):
        themaid = 'AGRYHMET'
        result1 = querydb.set_thema(themaid=themaid)
        if result1:
            if PRINT_RESULTS:
                print(result1)
            self.assertEqual(True, result1)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        themaid = 'JRC'
        result2 = querydb.set_thema(themaid=themaid)
        if result2:
            if PRINT_RESULTS:
                print(result2)
            self.assertEqual(True, result2)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_update_eumetcast_source_info(self):
        eumetcast_id = {'eumetcast_id': 'EO:EUM:DAT:PROBA-V:DMP'}
        eumetcastsource = crud_db_products.read('eumetcast_source', **eumetcast_id)

        eumetcastsourceinfo = {'eumetcast_id': eumetcastsource[0]['eumetcast_id'],
                               'filter_expression_jrc': eumetcastsource[0]['filter_expression_jrc'],
                               'description': eumetcastsource[0]['description'],
                               'typical_file_name': eumetcastsource[0]['typical_file_name'],
                               'frequency': eumetcastsource[0]['frequency'],
                               'datasource_descr_id': eumetcastsource[0]['eumetcast_id'],
                               'defined_by': eumetcastsource[0]['defined_by'],
                               'orig_eumetcast_id': eumetcastsource[0]['eumetcast_id']
                               }
        datasource_descr_id = {'datasource_descr_id': 'EO:EUM:DAT:PROBA-V:DMP'}
        datasourcedescr = crud_db_products.read('datasource_description', **datasource_descr_id)

        datasourcedescrinfo = {'datasource_descr_id': datasourcedescr[0]['datasource_descr_id'],
                               'format_type': datasourcedescr[0]['format_type'],
                               'file_extension': datasourcedescr[0]['file_extension'],
                               'delimiter': datasourcedescr[0]['delimiter'],
                               'date_format': datasourcedescr[0]['date_format'],
                               'date_position': datasourcedescr[0]['date_position'],
                               'product_identifier': datasourcedescr[0]['product_identifier'],
                               'prod_id_position': datasourcedescr[0]['prod_id_position'] if datasourcedescr[0]['prod_id_position'] != 'None' else 'NULL',
                               'prod_id_length': datasourcedescr[0]['prod_id_length'] if datasourcedescr[0]['prod_id_length'] != 'None' else 'NULL',
                               'area_type': datasourcedescr[0]['area_type'],
                               'area_position': datasourcedescr[0]['area_position'] if datasourcedescr[0]['area_position'] != 'None' else 'NULL',
                               'area_length': datasourcedescr[0]['area_length'] if datasourcedescr[0]['area_length'] != 'None' else 'NULL',
                               'preproc_type': datasourcedescr[0]['preproc_type'],
                               'product_release': datasourcedescr[0]['product_release'] if datasourcedescr[0]['product_release'] != 'None' else 'NULL',
                               'release_position': datasourcedescr[0]['release_position'] if datasourcedescr[0]['release_position'] != 'None' else 'NULL',
                               'release_length': datasourcedescr[0]['release_length'] if datasourcedescr[0]['release_length'] != 'None' else 'NULL',
                               'native_mapset': datasourcedescr[0]['native_mapset']}

        result = querydb.update_eumetcast_source_info(eumetcastsourceinfo, datasourcedescrinfo)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_update_ingest_subproduct_info(self):
        subproduct = {'productcode': 'chirps-dekad', 'subproductcode': '10d', 'version': '2.0'}
        subproductinfo = crud_db_products.read('product', **subproduct)

        ingestsubproductinfo = {'productcode': subproductinfo[0]['productcode'],
                                'version': subproductinfo[0]['version'],
                                'subproductcode': subproductinfo[0]['subproductcode'],
                                'orig_subproductcode': subproductinfo[0]['subproductcode'],
                                'descriptive_name': subproductinfo[0]['descriptive_name'] if subproductinfo[0]['descriptive_name'] != 'None' else 'NULL',
                                'description': subproductinfo[0]['description'] if subproductinfo[0]['description'] != 'None' else 'NULL',
                                'provider': subproductinfo[0]['provider'] if subproductinfo[0]['provider'] != 'None' else 'NULL',
                                'category_id': subproductinfo[0]['category_id'] if subproductinfo[0]['category_id'] != 'None' else 'NULL',
                                'defined_by': subproductinfo[0]['defined_by'] if subproductinfo[0]['defined_by'] != 'None' else 'NULL',
                                'activated': subproductinfo[0]['activated'],
                                'frequency_id': subproductinfo[0]['frequency_id'] if subproductinfo[0]['frequency_id'] != 'None' else 'NULL',
                                'date_format': subproductinfo[0]['date_format'] if subproductinfo[0]['date_format'] != 'None' else 'NULL',
                                'data_type_id': subproductinfo[0]['data_type_id'] if subproductinfo[0]['data_type_id'] != 'None' else 'NULL',
                                'scale_factor': subproductinfo[0]['scale_factor'] if subproductinfo[0]['scale_factor'] != 'None' else 'NULL',
                                'scale_offset': subproductinfo[0]['scale_offset'] if subproductinfo[0]['scale_offset'] != 'None' else 'NULL',
                                'nodata': subproductinfo[0]['nodata'] if subproductinfo[0]['nodata'] != 'None' else 'NULL',
                                'mask_min': subproductinfo[0]['mask_min'] if subproductinfo[0]['mask_min'] != 'None' else 'NULL',
                                'mask_max': subproductinfo[0]['mask_max'] if subproductinfo[0]['mask_max'] != 'None' else 'NULL',
                                'unit': subproductinfo[0]['unit'] if subproductinfo[0]['unit'] != 'None' else 'NULL',
                                'masked': subproductinfo[0]['masked'],
                                'timeseries_role': subproductinfo[0]['timeseries_role'] if subproductinfo[0]['timeseries_role'] != 'None' else 'NULL',
                                'display_index': subproductinfo[0]['display_index'] if subproductinfo[0]['display_index'] != 'None' else 'NULL'
                                }

        result = querydb.update_ingest_subproduct_info(ingestsubproductinfo)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_update_internet_source_info(self):
        internetsource_id = {'internet_id': 'UCSB:CHIRPS:PREL:DEKAD'}
        internetsource = crud_db_products.read('internet_source', **internetsource_id)

        internetsourceinfo = {'internet_id': internetsource[0]['internet_id'],
                              'orig_internet_id': internetsource[0]['internet_id'],
                              'defined_by': internetsource[0]['defined_by'],
                              'descriptive_name': internetsource[0]['descriptive_name'],
                              'description': internetsource[0]['description'],
                              'modified_by': internetsource[0]['modified_by'],
                              'url': internetsource[0]['url'],
                              'user_name': internetsource[0]['user_name'],
                              'password': internetsource[0]['password'],
                              'type': internetsource[0]['type'],
                              'include_files_expression': internetsource[0]['include_files_expression'],
                              'files_filter_expression': internetsource[0]['files_filter_expression'],
                              'status': internetsource[0]['status'],
                              'pull_frequency': internetsource[0]['pull_frequency'],
                              'frequency_id': internetsource[0]['frequency_id'],
                              'start_date': internetsource[0]['start_date'],
                              'end_date': internetsource[0]['end_date'],
                              'https_params': internetsource[0]['https_params'],
                              'datasource_descr_id': internetsource[0]['internet_id']}

        datasource_descr_id = {'datasource_descr_id': 'UCSB:CHIRPS:PREL:DEKAD'}
        datasourcedescr = crud_db_products.read('datasource_description', **datasource_descr_id)

        datasourcedescrinfo = {'datasource_descr_id': datasourcedescr[0]['datasource_descr_id'],
                               'format_type': datasourcedescr[0]['format_type'],
                               'file_extension': datasourcedescr[0]['file_extension'],
                               'delimiter': datasourcedescr[0]['delimiter'],
                               'date_format': datasourcedescr[0]['date_format'],
                               'date_position': datasourcedescr[0]['date_position'],
                               'product_identifier': datasourcedescr[0]['product_identifier'],
                               'prod_id_position': datasourcedescr[0]['prod_id_position'] if datasourcedescr[0]['prod_id_position'] != 'None' else 'NULL',
                               'prod_id_length': datasourcedescr[0]['prod_id_length'] if datasourcedescr[0]['prod_id_length'] != 'None' else 'NULL',
                               'area_type': datasourcedescr[0]['area_type'],
                               'area_position': datasourcedescr[0]['area_position'] if datasourcedescr[0]['area_position'] != 'None' else 'NULL',
                               'area_length': datasourcedescr[0]['area_length'] if datasourcedescr[0]['area_length'] != 'None' else 'NULL',
                               'preproc_type': datasourcedescr[0]['preproc_type'],
                               'product_release': datasourcedescr[0]['product_release'] if datasourcedescr[0]['product_release'] != 'None' else 'NULL',
                               'release_position': datasourcedescr[0]['release_position'] if datasourcedescr[0]['release_position'] != 'None' else 'NULL',
                               'release_length': datasourcedescr[0]['release_length'] if datasourcedescr[0]['release_length'] != 'None' else 'NULL',
                               'native_mapset': datasourcedescr[0]['native_mapset']}

        result = querydb.update_internet_source_info(internetsourceinfo, datasourcedescrinfo)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_update_processing_chain_products(self):
        # Input product definition
        productcode = 'chirps-dekad'
        version = '2.0'
        input_sprodcode = '10d'

        # Create 'manually' a proc_list (normally done by pipeline)
        proc_lists = functions.ProcLists()
        proc_lists.proc_add_subprod_group("10dstats")
        proc_lists.proc_add_subprod("10davg-TEST", "10dstats", final=False,
                                                   descriptive_name='10d Average',
                                                   description='Average rainfall for dekad',
                                                   frequency_id='e1dekad',
                                                   date_format='MMDD',
                                                   masked=False,
                                                   timeseries_role='10d',
                                                   active_default=True)

        if PRINT_RESULTS:
            for my_sprod in proc_lists.list_subprods:
                my_sprod.print_out()

        my_sprod = proc_lists.list_subprods[0]
        # Get input product info
        input_product_info = querydb.get_product_out_info(allrecs=False,
                                                          productcode=productcode,
                                                          subproductcode=input_sprodcode,
                                                          version=version)

        result = querydb.update_processing_chain_products(productcode, version, my_sprod, input_product_info)
        if result['success']:
            # delete new created subproduct
            product = {
                'productcode': 'chirps-dekad',
                'subproductcode': '10davg-TEST',
                'version': '2.0'
            }
            crud_db_products.delete('product', **product)

            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result['success'])
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!
            if PRINT_RESULTS:
                print(result['message'])

    def test_update_product_info(self):
        nativeproduct = {'productcode': 'chirps-dekad', 'subproductcode': 'chirps-dekad_native', 'version': '2.0'}
        nativeproductinfo = crud_db_products.read('product', **nativeproduct)

        nativeproductinfo = {'productcode': 'chirps-dekad-test',
                             'orig_productcode': nativeproductinfo[0]['productcode'],
                             'version': 'test',
                             'orig_version': nativeproductinfo[0]['version'],
                             'descriptive_name': nativeproductinfo[0]['descriptive_name'] if nativeproductinfo[0][
                                                                                                 'descriptive_name'] != 'None' else 'NULL',
                             'description': nativeproductinfo[0]['description'] if nativeproductinfo[0][
                                                                                       'description'] != 'None' else 'NULL',
                             'provider': nativeproductinfo[0]['provider'] if nativeproductinfo[0][
                                                                                 'provider'] != 'None' else 'NULL',
                             'category_id': nativeproductinfo[0]['category_id'] if nativeproductinfo[0][
                                                                                       'category_id'] != 'None' else 'NULL',
                             'defined_by': nativeproductinfo[0]['defined_by'] if nativeproductinfo[0][
                                                                                     'defined_by'] != 'None' else 'NULL',
                             'activated': nativeproductinfo[0]['activated']}

        result1 = querydb.update_product_info(nativeproductinfo)
        if result1:
            # change product back to original
            nativeproductinfo['productcode'] = 'chirps-dekad'
            nativeproductinfo['orig_productcode'] = 'chirps-dekad-test'
            nativeproductinfo['version'] = '2.0'
            nativeproductinfo['orig_version'] = 'test'
            result2 = querydb.update_product_info(nativeproductinfo)
            if PRINT_RESULTS:
                print(result1)
                print(result2)
            self.assertEqual(True, result1)
            self.assertEqual(True, result2)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_update_user_graph_tpl_drawproperties(self):
        # The default user_graph_templates for jrc_ref does not have user_graph_tpl_drawproperties,
        # so get the graph_tpl_id of a non default user_graph_templates for user jrc_ref
        query = "SELECT graph_tpl_id " \
                "FROM analysis.user_graph_templates " \
                "where userid = 'jrc_ref' " \
                "AND graph_tpl_name != 'default' " \
                "LIMIT 1"

        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        graph_tpl_id = queryresult[0]['graph_tpl_id']

        # Get the user_graph_tpl_drawproperties of the above found graph_tpl_id to use as sample data.
        user_graph_tpl_drawproperties = {'graph_tpl_id': graph_tpl_id}
        user_graph_tpl_drawpropertiesinfo = crud_db_analysis.read('user_graph_tpl_drawproperties', **user_graph_tpl_drawproperties)

        graphdrawprobs = {
            'graph_tpl_id': user_graph_tpl_drawpropertiesinfo[0]['graph_tpl_id'],
            'graph_type': user_graph_tpl_drawpropertiesinfo[0]['graph_type'],
            'graph_width': user_graph_tpl_drawpropertiesinfo[0]['graph_width'],
            'graph_height': user_graph_tpl_drawpropertiesinfo[0]['graph_height'],
            'graph_title': user_graph_tpl_drawpropertiesinfo[0]['graph_title'],
            'graph_title_font_size': user_graph_tpl_drawpropertiesinfo[0]['graph_title_font_size'],
            'graph_title_font_color': user_graph_tpl_drawpropertiesinfo[0]['graph_title_font_color'],
            'graph_subtitle': user_graph_tpl_drawpropertiesinfo[0]['graph_subtitle'],
            'graph_subtitle_font_size': user_graph_tpl_drawpropertiesinfo[0]['graph_subtitle_font_size'],
            'graph_subtitle_font_color': user_graph_tpl_drawpropertiesinfo[0]['graph_subtitle_font_color'],
            'legend_position': user_graph_tpl_drawpropertiesinfo[0]['legend_position'],
            'legend_font_size': user_graph_tpl_drawpropertiesinfo[0]['legend_font_size'],
            'legend_font_color': user_graph_tpl_drawpropertiesinfo[0]['legend_font_color'],
            'xaxe_font_size': user_graph_tpl_drawpropertiesinfo[0]['xaxe_font_size'],
            'xaxe_font_color': user_graph_tpl_drawpropertiesinfo[0]['xaxe_font_color']
        }
        graphtpl_info = {
            'userid': 'jrc_ref',
            'istemplate': 'false',
            'graph_tpl_id': '-1',
            'graph_tpl_name': 'default'
        }
        result = querydb.update_user_graph_tpl_drawproperties(graphdrawprobs, graphtpl_info)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

    def test_update_user_tpl_timeseries_drawproperties(self):
        # The default user_graph_templates for jrc_ref does not have user_graph_tpl_timeseries_drawproperties,
        # so get the graph_tpl_id and graph_tpl_name of a non default user_graph_templates for user jrc_ref
        query = "SELECT graph_tpl_id, graph_tpl_name, istemplate " \
                "FROM analysis.user_graph_templates " \
                "where userid = 'jrc_ref' " \
                "AND graph_tpl_name != 'default' " \
                "LIMIT 1"

        queryresult = dbschema_analysis.execute(query)
        queryresult = queryresult.fetchall()
        graph_tpl_id = queryresult[0]['graph_tpl_id']
        graph_tpl_name = queryresult[0]['graph_tpl_name']
        istemplate = queryresult[0]['istemplate']

        # Get the user_graph_tpl_timeseries_drawproperties of the above found graph_tpl_id to use as sample data.
        user_graph_tpl_timeseries_drawproperties = {'graph_tpl_id': graph_tpl_id}
        timeseries_drawpropertiesinfo = crud_db_analysis.read('user_graph_tpl_timeseries_drawproperties', **user_graph_tpl_timeseries_drawproperties)
        tsdrawproperties = {
            'userid': 'jrc_ref',
            'graph_tpl_id': timeseries_drawpropertiesinfo[0]['graph_tpl_id'],
            'graph_tpl_name': graph_tpl_name,
            'istemplate': istemplate,
            'productcode': timeseries_drawpropertiesinfo[0]['productcode'],
            'subproductcode': timeseries_drawpropertiesinfo[0]['subproductcode'],
            'version': timeseries_drawpropertiesinfo[0]['version'],
            'tsname_in_legend': timeseries_drawpropertiesinfo[0]['tsname_in_legend']+'_TEST',
            'charttype': timeseries_drawpropertiesinfo[0]['charttype'],
            'linestyle': timeseries_drawpropertiesinfo[0]['linestyle'],
            'linewidth': timeseries_drawpropertiesinfo[0]['linewidth'],
            'color': timeseries_drawpropertiesinfo[0]['color'],
            'yaxe_id': timeseries_drawpropertiesinfo[0]['yaxe_id']
        }

        # update existing
        result = querydb.update_user_tpl_timeseries_drawproperties(tsdrawproperties)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        # Change back to original values
        tsdrawproperties['tsname_in_legend'] = timeseries_drawpropertiesinfo[0]['tsname_in_legend']
        result2 = querydb.update_user_tpl_timeseries_drawproperties(tsdrawproperties)

        # Create new record
        tsdrawproperties['subproductcode'] = '1monthavg'
        result3 = querydb.update_user_tpl_timeseries_drawproperties(tsdrawproperties)
        if result3:
            if PRINT_RESULTS:
                print(result3)
            self.assertEqual(True, result3)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!

        # delete new created record
        tsdrawprops = {
            'graph_tpl_id': timeseries_drawpropertiesinfo[0]['graph_tpl_id'],
            'productcode': timeseries_drawpropertiesinfo[0]['productcode'],
            'subproductcode': '1monthavg',
            'version': timeseries_drawpropertiesinfo[0]['version']
        }
        crud_db_analysis.delete('user_graph_tpl_timeseries_drawproperties', **tsdrawprops)

    def test_update_yaxe(self):
        params = {
            "aggregation_max": '',
            "aggregation_min": '',
            "aggregation_type": 'mean',
            "id": 'ndvi',
            "max": '',
            "min": '',
            "opposite": 'true',
            "title": 'NDVI',
            "title_color": '#008000',
            "title_font_size": '20',
            "unit": '',
            "userid": 'jrc_ref',
            "istemplate": 'false',
            "graph_tpl_id": '-1',
            "graph_tpl_name": 'default',
            "graphtype": 'cumulative'
        }
        result = querydb.update_yaxe(params)
        if result:
            if PRINT_RESULTS:
                print(result)
            self.assertEqual(True, result)
        else:
            self.assertFalse(True)  # Test fails: result = False because of an exception error!


suite_querydb = unittest.TestLoader().loadTestsFromTestCase(TestQuerydb)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_querydb)

