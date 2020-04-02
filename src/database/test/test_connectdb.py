# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from future import standard_library

import unittest
# from config import es_constants
from database import connectdb

standard_library.install_aliases()


class TestConnectDB(unittest.TestCase):
    def test_connection_sqlsoup(self):
        # Connect and test schema
        connect_db = connectdb.ConnectDB(schema='analysis', usesqlsoup=True)
        schema = ("%s." % connect_db.schema) if connect_db.schema else ""

        self.assertEqual(schema, 'analysis.')

    def test_connection_no_sqlsoup(self):
        # Connect and test schema
        connect_db = connectdb.ConnectDB(usesqlsoup=False)
        schema = ("%s." % connect_db.schema) if connect_db.schema else ""

        self.assertEqual(schema, 'products.')


suite_connectdb = unittest.TestLoader().loadTestsFromTestCase(TestConnectDB)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite_connectdb)
