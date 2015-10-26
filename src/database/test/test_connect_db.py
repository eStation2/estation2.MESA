# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from config import es_constants

__author__ = "Jurriaan van 't Klooster"

from database import connectdb


class TestConnectDB(unittest.TestCase):
    def test_connection_sqlite(self):

        # Force Testing mode
        #es_constants.es2globals['db_test_mode'] = True
        # Connect and test schema
        connect_db = connectdb.ConnectDB(use_sqlite=True)
        schema = ("%s." % connect_db.schema) if connect_db.schema else ""

        self.assertEquals(schema, '')

    def test_connection_postgresql(self):

        # Force NOT in Testing mode
        #es_constants.es2globals['db_test_mode'] = False
        # Connect and test schema
        connect_db = connectdb.ConnectDB()
        schema = ("%s." % connect_db.schema) if connect_db.schema else ""

        self.assertEquals(schema, 'products.')
