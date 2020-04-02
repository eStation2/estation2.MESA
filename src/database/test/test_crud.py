# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from future import standard_library

import unittest
from config import es_constants
from database import crud
from database import querydb
from lib.python import functions

standard_library.install_aliases()

crud_db_products = crud.CrudDB(schema=es_constants.es2globals['schema_products'])
crud_db_analysis = crud.CrudDB(schema=es_constants.es2globals['schema_analysis'])


class TestCrud(unittest.TestCase):

    def test_read_with_where(self):
        product_key = {
            "productcode": 'vgt-ndvi',
            "subproductcode": 'ndvi-linearx2',
            "version": 'sv2-pv2.2'
        }
        self.assertEqual(len(crud_db_analysis.read('timeseries_drawproperties_new', **product_key)), 1)

    def test_crud(self):
        records = len(crud_db_products.read('date_format'))
        self.assertTrue(records > 0)

        record = {'date_format': 'TESTING123', 'definition': 'We are testing crud!'}
        crud_db_products.create('date_format', record)

        self.assertEqual(len(crud_db_products.read('date_format', date_format='TESTING123')), 1)

        record = {'date_format': 'TESTING123', 'definition': 'Updating this record!'}
        crud_db_products.update('date_format', record)

        self.assertEqual(len(crud_db_products.read('date_format')), records + 1)

        crud_db_products.delete('date_format', date_format='TESTING123')

        self.assertEqual(len(crud_db_products.read('date_format')), records)

        productinfo = {'productcode': 'vgt-fapar', 'subproductcode': 'vgt-fapar_native', 'version': 'V1.4', 'defined_by': 'TEST CRUD UPDATE', 'activated': True}
        crud_db_products.update('product', productinfo)

        produpdated = querydb.get_product_native(productcode='vgt-fapar', version='V1.4', allrecs=False)
        produpd = functions.dotdict(produpdated[0])
        self.assertEqual(produpd.activated, True)
        self.assertEqual(produpd.defined_by, 'TEST CRUD UPDATE')

        productinfo = {'productcode': 'vgt-fapar', 'subproductcode': 'vgt-fapar_native', 'version': 'V1.4', 'defined_by': 'JRC', 'activated': False}
        crud_db_products.update('product', productinfo)

        produpdated = querydb.get_product_native(productcode='vgt-fapar', version='V1.4', allrecs=False)
        produpd = functions.dotdict(produpdated[0])
        self.assertEqual(produpd.activated, False)
        self.assertEqual(produpd.defined_by, 'JRC')


suite_crud = unittest.TestLoader().loadTestsFromTestCase(TestCrud)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_crud)
