# -*- coding: utf-8 -*-
from __future__ import absolute_import
__author__ = "Jurriaan van 't Klooster"

import unittest
from config import es_constants
from database import crud
from database import querydb

crud_db = crud.CrudDB(schema=es_constants.es2globals['schema_products'])


class TestCrud(unittest.TestCase):

    def test_crud(self):
        records = len(crud_db.read('date_format'))
        self.assertTrue(records > 0)

        record = {'date_format': 'TESTING123', 'definition': 'We are testing crud!'}
        crud_db.create('date_format', record)

        self.assertEquals(len(crud_db.read('date_format', date_format='TESTING123')), 1)

        record = {'date_format': 'TESTING123', 'definition': 'Updating this record!'}
        crud_db.update('date_format', record)

        self.assertEquals(len(crud_db.read('date_format')), records + 1)

        crud_db.delete('date_format', date_format='TESTING123')

        self.assertEquals(len(crud_db.read('date_format')), records)

        productinfo = {'productcode': 'vgt_fapar', 'subproductcode': 'vgt_fapar_native', 'version': 'V1.3', 'defined_by': 'JRC', 'activated': False}
        crud_db.update('product', productinfo)

        produpdated = querydb.get_product_native(productcode='vgt_fapar', version='V1.3', allrecs=False, echo=False)
        self.assertEquals(produpdated.activated, False)

        productinfo = {'productcode': 'vgt_fapar', 'subproductcode': 'vgt_fapar_native', 'version': 'V1.3', 'defined_by': 'JRC', 'activated': True}
        crud_db.update('product', productinfo)

        produpdated = querydb.get_product_native(productcode='vgt_fapar', version='V1.3', allrecs=False, echo=False)
        self.assertEquals(produpdated.activated, True)
